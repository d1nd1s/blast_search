import subprocess
from dataclasses import dataclass
import logging
from typing import List

from dataclasses_json import dataclass_json
from lxml import etree
from scrapy.selector import Selector


@dataclass_json
@dataclass
class HitHSP:
    num: int
    bit_score: float
    score: int
    evalue: float
    query_from: int
    query_to: int
    hit_from: int
    hit_to: int
    query_frame: int
    hit_frame: int
    identity: int
    positive: int
    gaps: int
    align_len: int
    qseq: str
    midline: str
    hseq: str
    query_cover: str


@dataclass_json
@dataclass
class BlastHit:
    num: int
    hit_id: str
    hit_def: str
    accession: str
    hit_len: int
    hsps: List[HitHSP]


@dataclass_json
@dataclass
class FormParameters:
    max_target_sequences: int
    program_selection: str
    tax_id: str
    tax_id_neg: str
    short_query: int
    e_value: int
    word_size: int
    gapopen: int
    gapextend: int


@dataclass
class BlastResult:
    program: str
    db: str
    query_id: str
    query_def: str
    query_len: int
    hits: List[BlastHit]


def _parse_xml(xml_data):
    selector = Selector(
        text=xml_data,
        type='xml')

    hits = []
    for hit in selector.xpath('//Hit'):
        hsps = []
        for hsp in hit.xpath('.//Hsp'):
            midline = hsp.xpath('.//Hsp_midline/text()').get()
            query_cover = str(round((len(midline.replace(' ', ''))
                                     / len(midline)) * 100)) + '%'
            hsp = HitHSP(
                num=int(hsp.xpath('.//Hsp_num/text()').get()),
                bit_score=float(hsp.xpath('.//Hsp_bit-score/text()').get()),
                score=int(hsp.xpath('.//Hsp_score/text()').get()),
                evalue=float(hsp.xpath('.//Hsp_evalue/text()').get()),
                query_from=int(hsp.xpath('.//Hsp_query-from/text()').get()),
                query_to=int(hsp.xpath('.//Hsp_query-to/text()').get()),
                hit_from=int(hsp.xpath('.//Hsp_hit-from/text()').get()),
                hit_to=int(hsp.xpath('.//Hsp_hit-to/text()').get()),
                query_frame=int(hsp.xpath('.//Hsp_query-frame/text()').get()),
                hit_frame=int(hsp.xpath('.//Hsp_hit-frame/text()').get()),
                identity=int(hsp.xpath('.//Hsp_identity/text()').get()),
                positive=int(hsp.xpath('.//Hsp_positive/text()').get()),
                gaps=int(hsp.xpath('.//Hsp_gaps/text()').get()),
                align_len=int(hsp.xpath('.//Hsp_align-len/text()').get()),
                qseq=hsp.xpath('.//Hsp_qseq/text()').get(),
                hseq=hsp.xpath('.//Hsp_hseq/text()').get(),
                midline=midline,
                query_cover=query_cover
            )
            hsps.append(hsp)

        hit = BlastHit(
            num=int(hit.xpath('.//Hit_num/text()').get()),
            hit_id=hit.xpath('.//Hit_id/text()').get(),
            hit_def=hit.xpath('.//Hit_def/text()').get(),
            accession=hit.xpath('.//Hit_accession/text()').get(),
            hit_len=int(hit.xpath('.//Hit_len/text()').get()),
            hsps=hsps
        )
        hits.append(hit)

    result = BlastResult(
        program=selector.xpath('.//BlastOutput_program/text()').get(),
        db=selector.xpath('.//BlastOutput_db/text()').get(),
        query_id=selector.xpath('.//BlastOutput_query-ID/text()').get(),
        query_def=selector.xpath('.//BlastOutput_query-def/text()').get(),
        query_len=int(selector.xpath('.//BlastOutput_query-len/text()').get()),
        hits=hits
    )

    return result


class BlastRunner:
    def __init__(self,
                 program: str,
                 db_path: str,
                 ):
        self.program = program
        self.db_path = db_path

    def run(self, query_file, parameters) -> BlastResult:
        cmd = [
            self.program,
            '-query', query_file.name,
            '-db', self.db_path,
            '-outfmt', '5',
            '-max_target_seqs', str(parameters.max_target_sequences),
            '-task', parameters.program_selection,
            '-evalue', str(parameters.e_value),
            '-word_size', str(parameters.word_size),
            '-gapopen', str(parameters.gapopen),
            '-gapextend', str(parameters.gapextend)
        ]
        if parameters.tax_id:
            cmd.append('-taxids', parameters.tax_id)
        if parameters.tax_id_neg:
            cmd.append('-negative_taxids', parameters.tax_id_neg,)

        try:
            sp_run = subprocess.run(cmd,
                                    capture_output=True,
                                    encoding='utf-8',
                                    check=True)
        except subprocess.CalledProcessError as err:
            logging.error('Blast execution error: %s', err.stderr)
            return None

        dtd = etree.DTD(file='data/blastoutput_mod.dtd')
        tree = etree.XML(sp_run.stdout)

        if not dtd.validate(tree):
            logging.error('Error validating Blast output: %s',
                          dtd.error_log.filter_from_errors()[0])
            return None

        return _parse_xml(sp_run.stdout)
