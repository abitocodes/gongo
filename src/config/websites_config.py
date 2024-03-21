websites = [
    {
        "name": "KISA 한국인터넷진흥원>알림마당>공지사항",
        "url": "https://www.kisa.or.kr/401?page=1&searchDiv=30&searchWord=%EB%B8%94%EB%A1%9D%EC%B2%B4%EC%9D%B8&_csrf=e3d30d8e-8d61-4b41-b096-efef607dfcfb",
        "base_url": "https://www.kisa.or.kr",
        "selector": "tbody tr:not(.notice)", 
        "crawling": "true"
    },
    {
        "name": "국가과학기술지식정보서비스(NTIS)>국가R&D통합공고",
        "url": "https://www.ntis.go.kr/rndgate/eg/un/ra/mng.do",
        "base_url": "https://www.ntis.go.kr",
        "selector": "table.basic_list tbody tr",
        "crawling": "false"
    },
]
