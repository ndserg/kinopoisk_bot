class RequestError(Exception):
    """Класс кастомного исключиния для перехвата ошибок request/response от сервера.

    Attributes:
        __error_code: Код ошибки.
        __message: Причина ошибки.
        __error_text: Текст ошибки.
    """

    def __init__(self, error_code: str, message: str, error_text: str) -> None:
        self.__error_code = error_code
        self.__message = message
        self.__error_text = error_text

    def __str__(self) -> str:
        """Магический метод __str__ для вывода информации об ошибке.

        Returns:
            Строка с информацией об ошибке.
        """
        return f"{self.__message}\nError Code: {self.__error_code}\nError text: {self.__error_text}"
