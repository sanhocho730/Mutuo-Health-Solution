from typing import List, Optional, Union


class Fillable:
    pass


class Blank(Fillable):
    def __init__(self, blank: Optional[str] = None, prompt: str = '') -> None:
        self.blank: Optional[str] = blank
        self.prompt: str = prompt  # a string suggesting what to fill in the blank

    def __str__(self) -> str:
        result = ''
        if self.prompt:
            result += f'({self.prompt}) '
        result += self.blank if self.blank else '____'
        return result


class Option:
    def __init__(
        self,
        description: str = '',
        blank: Optional[Blank] = None,
        selected: Optional[bool] = None,
    ) -> None:
        self.description: str = description
        self.blank: Optional[Blank] = blank
        self.selected: Optional[bool] = selected

    def __str__(self) -> str:
        result = ''
        result += (
            '[v] ' if self.selected else ('[x] ' if self.selected is False else '[ ] ')
        )
        result += self.description
        if self.blank:
            result += f' {self.blank}'
        return result


class Choice(Fillable):
    def __init__(
        self, prompt: Optional[str] = None, options: List[Option] = []
    ) -> None:
        self.prompt: Optional[str] = prompt
        self.options: List[Option] = options

    def __str__(self) -> str:
        return f'{self.prompt}\n' + '\n'.join(map(str, self.options))


class Question:
    def __init__(self, content: List[Union[str, Blank, Choice]] = []) -> None:
        self.content: List[Union[str, Blank, Choice]] = content

    def __str__(self) -> str:
        return '\n'.join(map(str, self.content))


if __name__ == '__main__':
    print('Testing libquestion.py')
    q = Question(
        [
            '1. Medical Condition',
            Blank(),
            Choice(
                'Prognosis - condition is likely to:',
                [
                    Option('improve'),
                    Option('remain same'),
                    Option('deteriorate'),
                    # Option('unknown')
                    # Option("unknown, please specify", Blank())
                    Option('unknown, please specify', Blank(prompt='mm/dd/yyyy')),
                ],
            ),
            'Impairment(s)',
            Blank(),
            'Duration of Impairment(s) (mandatory - complete both columns)',
            Choice(
                'Expected to last:',
                [
                    Option('less than 1 year'),
                    Option('1 year or more'),
                ],
            ),
            Choice(
                'And is:',
                [
                    Option('recurrent/episodic'),
                    Option('continuous'),
                ],
            ),
            'Restriction(s)',
            Blank(),
        ]
    )
    print(q)
    print('\n')

    # q = [
    #     {
    #         'type': 'text',
    #         'content': '1. Medical Condition'
    #     },
    #     {
    #         'type': 'blank',
    #         'prompt': '',
    #     },
    #     {
    #         'type': 'choices',
    #         'prompt': 'Prognosis - condition is likely to:',
    #         'options': [
    #             {
    #                 'description': 'improve',
    #                 'has_blank': False,
    #             },
    #             {
    #                 'description': 'remain same',
    #                 'has_blank': False,
    #             },
    #             {
    #                 'description': 'deteriorate',
    #                 'has_blank': False,
    #             },
    #             {
    #                 'description': 'unknown',
    #                 'has_blank': False,
    #             }
    #         ]
    #     }
    # ]

    q.content[1].blank = 'Diabetes'
    # q.content[2].options[0].selected = True
    q.content[2].options[3].selected = True
    q.content[2].options[3].blank = '01/01/2024'
    q.content[4].blank = 'Hearing loss'
    q.content[6].options[1].selected = True
    q.content[7].options[0].selected = True
    q.content[9].blank = 'No lifting over 50 lbs'

    print(q)
