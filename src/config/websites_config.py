websites = [
    {
        "name": "KISA 한국인터넷진흥원 공지사항",
        "url": "https://www.kisa.or.kr/401",
        "base_url": "https://www.kisa.or.kr",
        "selector": "tbody tr:not(.notice)",  # 각 게시글의 행 전체를 선택
        "crawling": "true"
    },
    {
        "name": "국가과학기술지식정보서비스",
        "url": "https://www.ntis.go.kr/rndgate/eg/un/ra/mng.do",
        "base_url": "https://www.ntis.go.kr",
        "selector": ".notice_title",
        "crawling": "false"
    },
]
