# Academic_Drawing

## 하네스: Academic Drawing (graphical abstract + academic slides)

**목표:** 한 프로젝트의 아이디어/파이프라인/실험을 한 눈에 보여주는 publication-grade **graphical abstract**(먼저)와 그것을 재사용하는 **academic presentation deck**(다음)을, 하나의 팔레트·톤·인용 스타일로 일관되게 생산한다. 모든 산출물은 생성 → 기계적 QC → naive 리뷰(Codex) → 디자인 리뷰 → human confirm 루프를 거친다.

**트리거:** graphical abstract / 그래피컬 초록 / 요약 그림 / Cell·Nature 스타일 abstract figure, academic 발표 슬라이드 / 세미나 / 디펜스 자료 / experimental procedure 도식, 또는 이들의 재작업(다시/수정/보완/restyle/recolor/부분 재실행/export) 요청 시 → `academic-drawing-orchestrator` 스킬을 사용하라. 단순 질문은 직접 응답 가능.

**핵심 규칙 (요약 — 상세는 스킬에):**
- 색: `ga-style-contract/assets/palette.json`이 유일한 색 출처. 토큰 이름으로만 참조. 슬라이드당 ≤5 structural 색. 프로젝트 전체에서 condition→color 고정. 데이터 시리즈는 Okabe-Ito(CVD-safe). 팔레트 lock 시 `contrast_check.py`(WCAG+CVD+grayscale)가 sign-off 게이트.
- 텍스트: 절제된 학술 톤, AI-slop 금지, 환각/임의 약어·전문용어 금지. 약어 미상 시 → `csnl-ontology`로 검증 → 그래도 없으면 **Director의 in-chat 게이트**로 운영자에게 1문항(prediction-first) 질문 또는 `[PLACEHOLDER]`. **async interview/DM 캠페인 금지**(운영자는 이미 in-chat). 통계치·수식은 본문 최소화.
- 인용: `Author et al., YYYY` — **Zotero MCP에서 resolve**(`mcp__zotero__*` → `format_citation.py`). 손으로 인용 문자열 작성 금지; 못 찾으면 PLACEHOLDER + 게이트에서 질문.
- 수식: 4단계 게이트 — mathtext parse → sympy 기호/항등 검증(`equation_qc.py`) → Codex(모델 적절성) → vision(가독성). 작성자는 `_workspace/eqs.json` emit.
- 배치: text↔shape 겹침 금지 — `overlap-qc/scripts/overlap_check.py`가 하드 게이트(text-text / text-spill / clipped = FAIL). 슬라이드는 `pptx_style_lint.py`가 팔레트/라벨색/≤N-hue/폰트 하드 게이트.
- 범위: result figure, 코드 기반 plot, PDF crop 영역은 **placeholder**로 남긴다(내용 fabricate 금지).

**결정 규칙 (속도/토큰 최적화 — 새 세션은 이걸 먼저 따른다):** 오케스트레이터는 요청에서 **Fast / Standard / Full 모드를 스스로 판단**하고(묻지 않음), don't-ask 기본값(팔레트=활성 저널 프리셋 NPG, GA=Cell square, 슬라이드=16:9 PPTX, 조건=brief에서 추론, 인용=Zotero-or-PLACEHOLDER)으로 **바로 생성**한다. 리뷰는 **전수검사 금지** — `academic-drawing-orchestrator/references/routing-and-review.md`의 scope/routing/rule에 따라 **해당되는 리뷰만 near-final에 1회**(기계적 게이트 overlap/lint/equation만 항상). 그 파일이 "얼마나 할지"의 SoT. 단순/구조화 입력은 Fast(팀·preview·다중리뷰 생략).

**구성:** 에이전트/스킬 목록은 `.claude/agents/`, `.claude/skills/`와 오케스트레이터 스킬에서 관리(여기 중복 기재하지 않음). 실행 모드: 하이브리드(생성=에이전트 팀, 리뷰=병렬 서브에이전트). 모든 에이전트 `model: opus`.

**환경 프리플라이트(실행 전 확인):**
- `soffice`는 PATH에 없음 → **절대경로** `/Applications/LibreOffice.app/Contents/MacOS/soffice` 사용. headless Chrome도 절대경로(앱 번들).
- 슬라이드 엔진: **빌드=pptxgenjs**(`npm i -g pptxgenjs` 필요, 미설치), **lint=python-pptx**(설치됨 1.0.2, read-only). 충돌 없음.
- 확인됨: rsvg-convert·inkscape·cairosvg·headless Chrome·pdftoppm·matplotlib 3.10.8·seaborn 0.13.2·sympy 1.14·Codex CLI 0.125.0(인증)·Zotero MCP(2 libs, CSNL 포함). 선택: `pip install 'markitdown[pptx]'`(슬라이드 텍스트 QA).
- Cell GA 기본 = **square 1650px @300dpi, Arial 12–16pt, 1 panel**(공식). portrait은 `--target cell_portrait`(venue 허용 시만).

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-06-25 | 초기 구성 (graphical abstract + slides 하네스) | 전체 — 9 에이전트, 오케스트레이터 + ga-style-contract / overlap-qc / slide-rhetoric 신규 스킬, graphical-abstract·scientific-figure vendoring | 초기 구축 |
| 2026-06-25 | 최적화 통합 (다각도 조사 반영) | Zotero 인용 resolve(`format_citation.py`)·Codex 리뷰어 base-instructions/스키마·sympy 수식 게이트(`equation_qc.py`)·deck 스타일 lint(`pptx_style_lint.py`)·팔레트 contrast/CVD 게이트(`contrast_check.py`)·Cell GA square 정정 + PNAS 프리셋·interview→in-chat 게이트·design-reviewer SciGA 출처 | 7각도 조사 워크플로우 MUST/HIGH 반영 |
| 2026-06-25 | 인터뷰 결정 반영 | `logic-reviewer`·`slide-web-builder` 에이전트 신규(11 에이전트), 오케스트레이터 Phase 2.5(show_widget live preview)·GA aspect per-project·dual slide 빌더(PPTX+HTML web)·3-lens 리뷰(Codex/logic/design) | 운영자 인터뷰(T0) 결정: aspect=per-project, palette=muted+redundant, add-ons=live-preview+logic-lens, slides=둘다(pptx+web) |
| 2026-06-25 | 팔레트/폰트 수정 — 학술 저널 팔레트 도입 | `palette.json`에 ggsci journal_presets(npg/aaas/lancet/nejm/jama) 추가, **active=NPG(Nature)**: cond_a=teal #00A087, cond_b=navy #3C5488, accent=coral #E64B35, data_series=NPG순서. 신규 `academic_mpl.py`(Arial 강제+muted prop-cycle)·`render_presets.py`. plot은 일반 blue/orange 금지, 명명 condition은 label_map 토큰 사용 | "그림 색상이 claude스럽고 Nature/Cell 팔레트 미적용" 피드백 → NPG 저널 팔레트 lock |
| 2026-06-25 | 라우팅/모드 최적화 (1단계) | 신규 `references/routing-and-review.md`(Fast/Standard/Full 모드·don't-ask 기본값·선택적 리뷰 scope/routing/rule). 오케스트레이터: Decision-discipline 섹션·Phase 0 모드선택·Phase 3 선택적 리뷰·description 일반화(any project) | 새 세션 테스트 "느리고 decision uncertainty 큼" → 결정/리뷰 규칙 명시화. (진행중: 템플릿 라이브러리·일반화·deps 정돈·Codex 리뷰) |
