import subprocess
from dataclasses import dataclass, field
from typing import List

from scrapy.selector import Selector


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


@dataclass
class BlastHit:
    num: int
    hit_id: str
    hit_def: str
    accession: int
    hit_len: int
    hsps: List[HitHSP]


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
        for j, hsp in enumerate(hit.xpath('.//Hsp')):
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
            accession=int(hit.xpath('.//Hit_accession/text()').get()),
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
                 db_path: str):
        self.program = program
        self.db_path = db_path

    def run(self, query_file) -> BlastResult:

        cmd = [
            self.program,
            '-query', query_file.name,
            '-db', self.db_path,
            '-outfmt', '5'
        ]

        try:
            sp_run = subprocess.run(cmd,
                                    capture_output=True,
                                    encoding='utf-8',
                                    check=True)
        except subprocess.CalledProcessError as err:
            return None

        return _parse_xml(sp_run.stdout)