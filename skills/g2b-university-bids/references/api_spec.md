# 나라장터 입찰공고정보서비스 API 요약

- 데이터셋: 조달청_나라장터 입찰공고정보서비스 (공공데이터포털 15129394)
- 서비스: `BidPublicInfoService`
- 사용 오퍼레이션: `getBidPblancListInfoServcPPSSrch` (용역 입찰공고, 검색조건 조회)
- 요청 URL: `http://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServcPPSSrch`

> 조달청이 경로를 바꾸는 경우가 있다. 오류가 나면 공공데이터포털 데이터셋 페이지의
> '요청주소'를 확인해 `scripts/search_bids.py`의 `ENDPOINT`를 고친다.

## 요청 파라미터 (이 스킬에서 쓰는 것)

| 파라미터 | 설명 | 예 |
|---|---|---|
| serviceKey | 인증키 (디코딩 키) | 환경변수 |
| numOfRows | 페이지당 건수 | 100 |
| pageNo | 페이지 번호 | 1 |
| type | 응답 형식 | json |
| inqryDiv | 조회구분. 1 = 공고게시일시, 3 = 변경일시 | 1 |
| inqryBgnDt / inqryEndDt | 조회 시작·종료 (YYYYMMDDHHMM) | 202610150000 |
| dminsttNm | 수요기관명 (부분일치) | 대학 |
| bidNtceNm | 공고명 (부분일치) | 발전계획 |

## 응답 필드 (사용하는 것)

| 필드 | 의미 |
|---|---|
| bidNtceNo / bidNtceOrd | 공고번호 / 차수 (정정 시 차수 증가) |
| bidNtceNm | 공고명 |
| ntceInsttNm / dminsttNm | 공고기관 / 수요기관 (조달청 대행 공고는 공고기관이 조달청) |
| bidNtceDt / bidClseDt | 공고일시 / 입찰마감일시 |
| asignBdgtAmt / presmptPrce | 배정예산 / 추정가격 (예산은 배정예산 우선) |
| cntrctCnclsMthdNm | 계약방법 (협상에 의한 계약 = 제안서 평가형) |
| bidNtceDtlUrl | 나라장터 공고 상세 링크 |

## 자주 나는 오류

| 코드 | 원인 | 조치 |
|---|---|---|
| 03 | 데이터 없음 | 정상. 기간을 넓혀 본다 |
| 20 / 30 | 키 미승인·오류 | 활용신청 승인 여부, 디코딩 키 사용 여부 확인 |
| 22 | 일일 트래픽 초과 | 다음 날 재실행 |
| 기간 오류 | 조회기간 초과 | 스크립트는 7일 단위로 나눠 호출함 |
