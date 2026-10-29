# 🎓 g2b-university-bids: 나라장터 대학 발주 사업 자동 검색 Skill

> 매주 나라장터에 들어가 '대학'을 검색하고, 청소·시설 공고를 걸러내고, 쓸 만한 공고를 엑셀에 옮기던 일을 Claude Skill 하나로 자동화했습니다.

## 어떤 문제를 푸나

| Before (수작업) | After (Skill) |
|---|---|
| 나라장터 접속 후 기관명으로 반복 검색 | "이번 주 대학 공고 찾아줘" 한 마디 |
| 정정공고가 중복으로 보임 | 공고번호별 최신 차수만 남김 |
| 청소·경비·공사 공고가 대부분 | 키워드 점수로 A/B/C 자동 분류 |
| 예산을 보고 규모를 암산 | 예산 ÷ 1MM 단가 = 환산MM 자동 계산 |
| 엑셀 정리 후 팀 공유 | MD 브리프 + CSV(엑셀 호환) 자동 생성 |
| KAIST·UNIST 같은 과학기술원 누락 | '대학' + '과학기술원' 이중 검색 |

## 하네스 엔지니어링 6가지 구조 적용

`SKILL.md`의 섹션 ①~⑥이 그대로 6가지 구조입니다.

| # | 구조 | 이 스킬에서의 구현 |
|---|---|---|
| ① | **역할과 목표** | 수주 리서치 애널리스트. 성공 기준 "파트너가 5분 안에 검토 공고 선택" |
| ② | **컨텍스트** | 기간·키워드·예산·단가 기본값 표 + `references/` (API 명세, 점수 기준)를 필요할 때만 로드 |
| ③ | **도구** | `scripts/search_bids.py` (공식 Open API, 표준 라이브러리만 사용) |
| ④ | **실행 절차** | 조건 확정 → 키 확인 → 검색 → 결과 읽기 → 코멘트 → 전달의 6단계 |
| ⑤ | **가드레일** | API 값만 사실로 기재, 인증키 비노출, 호출량 제한, 스크래핑 금지, 판단은 사람에게 |
| ⑥ | **검증과 피드백** | 0건 원인 구분, 링크 대조, 중복 점검, 오분류 시 키워드 사전 보정 루프 |

## 폴더 구조

```
g2b-university-bids/
├── README.md
├── .gitignore
├── skills/g2b-university-bids/
│   ├── SKILL.md                  # 스킬 본문 (6가지 구조)
│   ├── scripts/search_bids.py    # 검색·필터·점수화·리포트
│   ├── references/
│   │   ├── api_spec.md           # 나라장터 API 요약
│   │   └── scoring.md            # A/B/C 등급 기준·키워드 사전
│   └── templates/brief_template.md
└── examples/
    ├── sample_response.json      # 가상 API 응답 (키 없이 테스트)
    ├── univ_bids_20261029.md     # 실행 결과 예시
    └── univ_bids_20261029.csv
```

## 설치

1. **인증키 발급**: [공공데이터포털](https://www.data.go.kr) 가입 → "조달청_나라장터 입찰공고정보서비스" 검색 → 활용신청 → 마이페이지에서 **디코딩 키** 복사
2. **Claude에 스킬 등록**
   - Claude 앱: `skills/g2b-university-bids` 폴더를 zip으로 묶어 설정 > 기능 > 스킬에서 업로드
   - Claude Code: 폴더를 `~/.claude/skills/`에 복사
3. **키 설정**: `export G2B_SERVICE_KEY="발급받은_디코딩_키"`

## 사용

Claude에게 이렇게 말하면 됩니다.

- "이번 주 나라장터 대학 공고 찾아줘"
- "최근 한 달 대학 발주 중 발전계획 관련, 1억 이상만"
- "대학병원 ISMP 공고 있어?"

직접 실행:

```bash
cd skills/g2b-university-bids/scripts
python search_bids.py --days 14
python search_bids.py --days 30 --keyword 발전계획 --min-budget 100000000
python search_bids.py --sample ../../../examples/sample_response.json   # 키 없이 시연
```

## 실행 결과 예시 (가상 데이터)

`examples/sample_response.json`의 9건을 넣으면 정정공고 중복과 비대학 공고를 제거해 7건을 남기고, A등급 5건을 골라냅니다. 청소·유지보수 공고는 C등급으로 분리됩니다. 결과는 [`examples/univ_bids_20261029.md`](examples/univ_bids_20261029.md)에 있습니다.

## 실제 운영과 피드백 루프 (⑥ 구조 실증)

2026-10-29에 실제 API로 최근 7일을 조회한 뒤, 결과를 사람이 검토하고 사전을 보정했습니다.

| | v1 | v2 (보정 후) |
|---|---|---|
| 대학 발주 공고 | 265건 | 243건 (재공고 중복·비대학 기관 제거) |
| A등급 | 32건 (대부분 SI·행사·운영대행) | **8건** |
| 수작업으로 고른 실제 후보 6건 포함 여부 | 일부는 B·C등급에 묻힘 | 6건 모두 A등급 |

주요 보정 내용은 다음과 같습니다. 자세한 내용은 [`references/scoring.md`](skills/g2b-university-bids/references/scoring.md)의 보정 이력에 있습니다.
- KAIST의 'AI'가 매칭되는 문제는 영문 약어를 단어 단위로 비교해 해결
- '[대학혁신지원사업]' 같은 예산 태그는 가중치를 낮춤
- 행사·연수·운영대행·병원 지원 업무를 제외어로 추가
- '체계 구축'·'방안 수립'처럼 컨설팅형 표현을 핵심어로 추가

## 한계와 다음 단계

- 점수는 **공고명 키워드 기반**입니다. 제안요청서 본문 분석은 아직 하지 않습니다.
- 다음 단계: 사전규격 공개(`getPublicPrcureThngInfoServcPPSSrch`) 조회를 추가해 본공고 전에 미리 포착하기, 매주 월요일 자동 실행

## 출처

- 조달청_나라장터 입찰공고정보서비스, 공공데이터포털 데이터셋 15129394
