index.html은 임의의 데이터추출사용으로 확인가능하지만
index copy.html은 윈도우 보안문제로 가상서버에서만 확인가능
vscode에서 오른쪽하단 golive 실행 폴더단위이기에 오픈폴더 꼭 하기
post.json파일 관리가 꼭 필요

firebase 사용법
*이건 개발환경의 첫번째로 딱한번만 하면 됨*
도구설치 ** 중요 경로가 현재 구현된 파일 내에 있어야함
npm install -g firebase-tools

firebase login
로그인 후 구글계정 선택

"Allow Firebase to collect..." 물어보면 Y 또는 N (상관없음) 입력 후 엔터.

인터넷 창이 열리면서 구글 로그인 화면이 나옵니다. 사용할 구글 계정으로 로그인하고 "허용"을 누르세요.

터미널에 "Success! Logged in as..."가 뜨면 성공!

그전에 firebase 내에 프로젝트 생성
-----------------------------------------------------------
프로젝트 초기화
firebase init
Hosting 선택
스페이스바 -> 엔터
Use an existing project
public 폴더 사용
N
N

파일 이사하기
public 내에 중요 파일들 복사

firebase deploy
하면 끝(무조건 index파일이어야함)

수정
public내에 있는 파일 수정해야함 꼭
저장 후 
firebase deploy
재배포

사이트 비활성화
firebase hosting:disable