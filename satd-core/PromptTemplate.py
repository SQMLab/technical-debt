from util import get_first_n_line, get_last_n_line
from jinja2 import Template


class PromptTemplate:
    def __init__(self, name, definition, instruction, n_shot_template, n_shot_answer_template, line_m_before, line_n_after):
        self._name = name
        self._definition = definition
        self._instruction = instruction
        self._n_shot_template = n_shot_template
        self._n_shot_answer_template = n_shot_answer_template
        self._line_m_before = line_m_before
        self._line_n_after = line_n_after

    @property
    def name(self):
        return self._name

    @property
    def definition(self):
        return self._definition

    @property
    def instruction(self):
        return self._instruction

    @property
    def line_m_before(self):
        return self._line_m_before

    @property
    def line_n_after(self):
        return self._line_n_after

    @property
    def shot_template(self):
        return self._n_shot_template

    def create_example(self, args):
        return self.resolve_template(args, self.shot_template)

    def create_answer(self, args):
        return self.resolve_template(args, self._n_shot_answer_template)

    def resolve_template(self, args, formula:str):
        properties = dict(args)
        if 'code_before' in properties:
            properties['code_before'] = get_last_n_line(args['code_before'], self.line_m_before)
        if 'code_after' in properties:
            properties['code_after'] = get_first_n_line(args['code_after'], self.line_n_after)
        return Template(formula).render(**properties)

    def create_prompt(self, examples: [str]):
        return self.definition + "\n" + self.instruction + "\n" + "\n" + "\n\n".join(examples)

    def __repr__(self):
        return f"PromptTemplate(name={self.name}, description='{self.definition}', example='{self.shot_template}')"