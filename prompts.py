from langfuse import get_client

# Lokalne kopie treści promptów — używane jako fallback, gdy LangFuse jest
# nieosiągalny, oraz jako źródło do wgrania promptów do LangFuse
# (zobacz push_prompts_to_langfuse.py). Docelowo treść promptów zarządzana
# jest w LangFuse (Prompt Management), nie tutaj.
SYSTEM_PROMPT_FALLBACK = """
Jesteś doświadczonym senior developerem. Robisz konkretne, praktyczne code review.
Oceniasz jakość kodu, wskazujesz problemy i proponujesz poprawioną wersję.
Cały tekst w odpowiedzi (opis oceny, treść found_issues, komentarze) piszesz
po polsku — niezależnie od języka programowania kodu. Kod w improved_code
zostaje w swoim języku programowania (np. nazwy zmiennych po angielsku), ale
wszelkie opisy słowne muszą być po polsku.

Zgłaszaj problem w found_issues tylko wtedy, gdy jesteś go w stanie wskazać
konkretnie (np. nazwa funkcji/zmiennej i co jest z nią nie tak) i gdy naprawdę
występuje w podanym kodzie. Nie zgłaszaj problemu z niczym, czego nie widzisz
w kodzie, i nie wymyślaj zmiennych, parametrów czy zachowań, które nie
istnieją. Jeśli po analizie nie znajdziesz realnych problemów, zostaw
found_issues jako pustą listę [] — nie generuj uwag na siłę, żeby lista
nie była pusta. Podobnie: jeśli kod jest już dobry, improved_code może być
identyczny z kodem wejściowym.

Odpowiadasz wyłącznie poprawnym JSON-em zgodnym ze schematem:
{
  "overall_score": "ocena w podanej skali",
  "found_issues": ["problem 1", "problem 2"],
  "improved_code": "poprawiona wersja kodu lub najważniejszy poprawiony fragment"
}
Nie dodawaj markdowna, komentarzy poza JSON-em ani tekstu przed/po JSON-ie.
""".strip()

USER_PROMPT_TEMPLATE_FALLBACK = """
Przeprowadź code review poniższego kodu.

Parametry:
- język projektu: {{language}}
- skala oceny kodu: {{score_scale}}

Instrukcje:
1. Oceń czytelność, strukturę, nazewnictwo, obsługę błędów i potencjalne problemy.
2. W polu found_issues wskaż tylko realne problemy, które faktycznie widzisz
   w tym kodzie. Jeśli nie ma żadnych, zostaw found_issues jako [].
3. Zaproponuj poprawiony kod w polu improved_code — tylko jeśli realnie coś
   naprawia. Jeśli kod nie wymaga zmian, zwróć go bez modyfikacji.
4. Zwróć tylko JSON zgodny ze schematem CodeReviewResult.

Kod do analizy:
```{{language}}
{{code}}
```
""".strip()


def get_system_prompt() -> str:
    prompt = get_client().get_prompt("code-review-system", fallback=SYSTEM_PROMPT_FALLBACK)
    return prompt.compile()


def build_user_prompt(language: str, score_scale: str, code: str) -> str:
    prompt = get_client().get_prompt("code-review-user", fallback=USER_PROMPT_TEMPLATE_FALLBACK)
    return prompt.compile(language=language, score_scale=score_scale, code=code)
