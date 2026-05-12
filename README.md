## ⚙ Git-flow
### 예시) feature/작업내용을 바로 알 수 있는 제목
### master develop 브랜치 뒤에는 예외상황이 아니면 '/작업제목'를 추가하지 않는다.

- master: 라이브 서버용 브랜치.
- develop: 추가 버전을 대비하여 개발하는 브랜치.
- feature: 추가 기능 개발 브랜치.
- hotfix: master 브랜치에서 발생한 버그를 수정하는 브랜치.

## 🎲 conventional commits
### 예시) [feature/1] 기능 구현

- github 이슈 생성 "[브랜치명] 작업내용"
- [브랜치명/이슈번호] 로 브랜치 생성
- 커밋 메시지는 "[브랜치명/이슈번호] 커밋 메세지" 형식으로 작성
- feature 브랜치에서 develop 브랜치로 PR 생성
- [Sourcetree](https://zerobin-dev.tistory.com/45)를 사용하면 편리함.
