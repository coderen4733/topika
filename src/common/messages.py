class AUTH_MESSAGES:
    class SIGN_UP:
        SUCCESS = "회원가입이 완료되었습니다."

        class FAIL:
            DUPLICATE = "이미 가입된 이메일입니다."

    class SIGN_IN:
        SUCCESS = "로그인에 성공했습니다."

        class FAIL:
            INVALID = "이메일 또는 비밀번호가 일치하지 않습니다."

    class RE_TOKEN:
        SUCCESS = "액세스토큰 재발급에 성공했습니다."


class USER_MESSAGES:
    class CREATE:
        SUCCESS = "회원생성에 성공했습니다."

        class FAIL:
            DUPLICATE = "이미 가입된 이메일입니다."

    class READ_ALL:
        SUCCESS = "회원 목록 조회에 성공했습니다."

    class READ_DETAIL:
        SUCCESS = "회원 상세 조회에 성공했습니다."

    class READ_ME:
        SUCCESS = "내 정보 조회에 성공했습니다."

    class UPDATE:
        SUCCESS = "회원 정보 수정에 성공했습니다."

        class FAIL:
            UNAUTHORIZED = "권한이 없습니다."

    class DELETE:
        SUCCESS = "회원 정보 삭제에 성공했습니다."

        class FAIL:
            UNAUTHORIZED = "권한이 없습니다."
