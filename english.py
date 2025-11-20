# -*- coding: utf-8 -*-
"""
Aktionsart detector (EN version)
--------------------------------
A faithful adaptation of the user's Spanish program for English.
- Prompts and diagnostics are phrased in English.
- Core logic and interaction flow are preserved.
- Tests used: causativity paraphrase; stativity (answer to "What happened?");
  punctuality via compatibility with a past progressive + "for an hour";
  telicity via "was V‑ing and suddenly stopped V‑ing → has V‑ed" entailment;
  dynamicity via compatibility with manner adverbs (vigorously / forcefully / with effort).

Notes:
- Keep infinitive, gerund, and past participle as user inputs (English morphology is irregular).
- Person/number selection uses the same 1s/2s/3s/1p/2p/3p scheme for auxiliary agreement.
- The program calls an LS module at the end (ls_en.py by default). Adjust `LS_SCRIPT`
  if you prefer a different filename.
"""
import locale
import logging
import os
import readline
import subprocess
import time
import sys
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Sequence, Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ------------------------- Config -------------------------
LS_SCRIPT = "ls_en.py"  # change to your logical-structure script if needed

class Answer(Enum):
    YES = ["yes", "y"]
    NO = ["no", "n"]


class Aktionsart(Enum):
    STATE = "state"
    CAUSATIVE_STATE = "causative state"
    ACHIEVEMENT = "achievement"
    CAUSATIVE_ACHIEVEMENT = "causative achievement"
    SEMELFACTIVE = "semelfactive"
    CAUSATIVE_SEMELFACTIVE = "causative semelfactive"
    ACTIVE_ACCOMPLISHMENT = "active accomplishment"
    CAUSATIVE_ACTIVE_ACCOMPLISHMENT = "causative active accomplishment"
    ACCOMPLISHMENT = "accomplishment"
    CAUSATIVE_ACCOMPLISHMENT = "causative accomplishment"
    ACTIVITY = "activity"
    CAUSATIVE_ACTIVITY = "causative activity"
    PROCESS = "process"
    CAUSATIVE_PROCESS = "causative process"


@dataclass
class Features:
    causative: bool = False
    stative: bool = False
    punctual: bool = False
    telic: bool = False
    dynamic: bool = False


@dataclass
class ClauseData:
    gerund: str = ""
    participle: str = ""
    subject: str = ""
    postverbal: str = ""
    person_number: str = ""
    got_forms: bool = False


# Auxiliaries for English agreement
BE_PRESENT = {
    '1s': "am",
    '2s': "are",
    '3s': "is",
    '1p': "are",
    '2p': "are",
    '3p': "are"
}

BE_PAST = {
    '1s': "was",
    '2s': "were",
    '3s': "was",
    '1p': "were",
    '2p': "were",
    '3p': "were"
}

HAVE_PRESENT = {
    '1s': "have",
    '2s': "have",
    '3s': "has",
    '1p': "have",
    '2p': "have",
    '3p': "have"
}


def set_english_locale():
    english_locales = ['en_US.UTF-8', 'en_GB.UTF-8', 'en.UTF-8', '']
    for loc in english_locales:
        try:
            return locale.setlocale(locale.LC_ALL, loc)
        except locale.Error:
            continue
    return locale.setlocale(locale.LC_ALL, '')


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def restart_message() -> None:
    print("\nIt is not possible to identify the aktionsart of the clause with these parameters.")
    print("Please review your answers carefully.")


def prompt_user(prompt: str) -> str:
    readline.set_startup_hook(lambda: readline.insert_text(""))
    try:
        if "\n" in prompt or len(prompt) > 60:
            print(prompt, end="", flush=True)
            user = input().strip()
        else:
            user = input(prompt).strip()
        return user.encode('utf-8').decode('utf-8')
    finally:
        readline.set_startup_hook()


def yes_no(question: str) -> bool:
    while True:
        try:
            ans = prompt_user(question).lower()
            if ans in Answer.YES.value:
                return True
            elif ans in Answer.NO.value:
                return False
            print("\nPlease answer 'yes (y)' or 'no (n)'.")
        except Exception as e:
            logging.error(f"Error getting answer: {e}")


def multiple_choice(question: str, options: Sequence[Union[str, Sequence[str]]], suffix: str) -> str:
    while True:
        try:
            ans = prompt_user(f"{question} {suffix}").lower()
            for opt in options:
                if isinstance(opt, Sequence) and not isinstance(opt, str):
                    if ans in opt:
                        return opt[0]
                elif ans == opt:
                    return opt
            print("\nPlease type a valid option.")
        except Exception as e:
            logging.error(f"Error getting answer: {e}")


def collect_clause_info(clause: str, data: ClauseData) -> ClauseData:
    data.gerund = prompt_user(f"\nType the GERUND of the verb in '{clause}' (e.g., 'melting', 'telling'): ")
    data.participle = prompt_user(f"Type the PAST PARTICIPLE (e.g., 'melted', 'told'): ")
    subj_in = prompt_user(f"Type everything that comes BEFORE the verb in '{clause}' (0 if nothing): ")
    data.subject = "" if subj_in == "0" else subj_in
    post_in = prompt_user(f"Type everything that comes AFTER the verb in '{clause}' (0 if nothing): ")
    data.postverbal = "" if post_in == "0" else post_in
    pn_question = "Type the person and number of the verb"
    pn_suffix = "(1s/2s/3s/1p/2p/3p): "
    pn_options: List[str] = ['1s', '2s', '3s', '1p', '2p', '3p']
    data.person_number = multiple_choice(pn_question, pn_options, pn_suffix)
    data.got_forms = True
    return data


def build_prog(past: bool, data: ClauseData) -> str:
    be = BE_PAST[data.person_number] if past else BE_PRESENT[data.person_number]
    parts = [data.subject, f"{be} {data.gerund}", data.postverbal]
    return " ".join(p for p in parts if p)


def build_perfect(data: ClauseData) -> str:
    have = HAVE_PRESENT[data.person_number]
    parts = [data.subject, f"{have} {data.participle}", data.postverbal]
    return " ".join(p for p in parts if p)


def build_stop(data: ClauseData) -> str:
    # Neutral: subject + stopped + V‑ing (+ postverbal)
    parts = [data.subject or "(subject)", f"stopped {data.gerund}", data.postverbal]
    return " ".join(p for p in parts if p)


# ------------------------- Diagnostics -------------------------

def causativity_test(clause: str) -> bool:
    print("\nCAUSATIVITY TEST")
    print(f"\nTry to paraphrase '{clause}' following these models: ")
    print("• The cat broke the vase → The cat CAUSED the vase to break")
    print("• Ana gave Pepe a book → Ana CAUSED Pepe to have a book")
    paraphrase = prompt_user("\nType your paraphrase (or '0' if not possible): ")
    if paraphrase == '0' or not paraphrase.strip():
        return False
    print("\nConsider the following:")
    cap = paraphrase[0].upper() + paraphrase[1:]
    print(f"• '{cap}' should preserve the meaning of '{clause}'.")
    print(f"• '{cap}' must not add new arguments nor duplicate existing ones in '{clause}'.")
    print("• Exclude consumption ('eat an apple') and creation ('write a story') readings.")
    return yes_no(f"\nDoes '{cap}' meet these criteria? (y/n): ")


def get_basic_event() -> str:
    while True:
        ev = prompt_user("\nType the resulting event/state without the cause (e.g., 'the vase broke', 'Pepe has a book').\nIf none comes to mind, type '0': ")
        if ev == "0" or ev.strip():
            return ev
        print("\nPlease enter a valid clause or '0'.")


def stativity_test(clause: str) -> bool:
    print("\nSTATIVITY TEST")
    return not yes_no(
        f"\nConsider the following dialogue:"
        f"\n—What happened a moment ago / yesterday / last month?"
        f"\n—{clause[0].upper() + clause[1:]}."
        f"\n\nDo you think '{clause}' is a good answer to that question (for at least one time option)? (y/n): ")


def dynamicity_test(data: ClauseData) -> bool:
    prog = build_prog(False, data)
    print("\nDYNAMICITY TEST")
    return yes_no(
        f"\nConsider: '{prog[0].upper() + prog[1:]} vigorously / forcefully / with effort'."
        f"\nIs this acceptable with at least one of the options? (y/n): ")


def punctuality_test(data: ClauseData) -> bool:
    prog_past = build_prog(True, data)
    print("\nPUNCTUALITY TEST")
    return yes_no(
        f"\nConsider: '{prog_past[0].upper() + prog_past[1:]} for an hour / for a month'."
        f"\nIs this expression acceptable (with at least one option) WITHOUT forcing an iterative or imminent reading? (y/n): ")


def telicity_test(data: ClauseData) -> bool:
    prog = build_prog(False, data)
    stop_expr = build_stop(data)
    perfect = build_perfect(data)
    print("\nTELICITY TEST")
    q = (f"\nImagine that {prog} and suddenly {stop_expr}."
         f"\nWould it then be true to say: '{perfect}'? (y/n): ")
    return not yes_no(q)


# ------------------------- Classification -------------------------

def determine_subtype(feats: Features) -> Optional[str]:
    if feats.stative:
        return "STATE"
    elif feats.punctual and feats.telic:
        return "ACHIEVEMENT"
    elif feats.punctual and not feats.telic:
        return "SEMELFACTIVE"
    elif not feats.punctual and feats.telic and feats.dynamic:
        return "ACTIVE_ACCOMPLISHMENT"
    elif not feats.punctual and not feats.telic and feats.dynamic:
        return "ACTIVITY"
    elif not feats.punctual and feats.telic and not feats.dynamic:
        return "ACCOMPLISHMENT"
    elif not feats.punctual and not feats.telic and not feats.dynamic:
        return "PROCESS"
    else:
        return None


def determine_aktionsart(feats: Features) -> Optional[Aktionsart]:
    sub = determine_subtype(feats)
    if sub is None:
        return None
    if feats.causative:
        return Aktionsart[f"CAUSATIVE_{sub}"]
    else:
        return Aktionsart[sub]


# ------------------------- Orchestration -------------------------

def obtain_features(clause: str, data: ClauseData) -> Union[Features, None]:
    feats = Features()
    data.got_forms = False

    caused = causativity_test(clause)
    if caused:
        basic_event = get_basic_event()
        if basic_event == "0":
            feats.causative = False
            print("\nPredicate is [-causative]")
        else:
            feats.causative = True
            print("\nPredicate is [+causative]")
            clause = basic_event
    else:
        feats.causative = False
        print("\nPredicate is [-causative]")

    time.sleep(0.5)

    feats.stative = stativity_test(clause)
    print(f"\nPredicate is [{'+' if feats.stative else '-'}stative]")
    time.sleep(0.5)

    if not feats.stative:
        collect_clause_info(clause, data)

        # Punctuality: if it is NOT compatible with durational for-phrases in past progressive → punctual = True
        feats.punctual = not punctuality_test(data)
        print(f"\nPredicate is [{'+' if feats.punctual else '-'}punctual]")
        time.sleep(0.5)

        feats.telic = telicity_test(data)
        print(f"\nPredicate is [{'+' if feats.telic else '-'}telic]")
        time.sleep(0.5)

        feats.dynamic = dynamicity_test(data)
        print(f"\nPredicate is [{'+' if feats.dynamic else '-'}dynamic]")
        time.sleep(0.5)

    return feats


def show_result(original_clause: str, akt: Aktionsart, feats: Features) -> None:
    print("\nRESULT")
    print(f"\nThe aktionsart of the predicate in '{original_clause}' is {akt.value.upper()}.")

    is_state = akt in [Aktionsart.STATE, Aktionsart.CAUSATIVE_STATE]

    feat_str = [
        f"[{'+' if feats.causative else '-'}causative]",
        f"[{'+' if feats.stative else '-'}stative]",
        f"[{'+' if (not is_state and feats.punctual) else '-'}punctual]",
        f"[{'+' if (not is_state and feats.telic) else '-'}telic]",
    ]

    if is_state:
        feat_str.append("[-dynamic]")
        is_dyn = False
    else:
        feat_str.append(f"[{'+' if feats.dynamic else '-'}dynamic]")
        is_dyn = feats.dynamic

    print("\nThis predicate is classified as such because it shows the following features:")
    print(' '.join(feat_str))

    # Logical structure option: currently disabled
    # if yes_no("\nWould you like to obtain the logical structure of this clause? (y/n): "):
    #     print("\nRunning the selected option...")
    #     time.sleep(1)
    #     run_ls(akt, original_clause, is_dyn)


def run_ls(akt: Aktionsart, original_clause: str, is_dynamic: bool) -> None:
    """
    Call the logical structure module (ls_en.py).
    Currently disabled until ls_en.py is implemented.
    """
    try:
        dyn_str = "dynamic" if is_dynamic else "non_dynamic"
        cmd = [sys.executable, "-u", LS_SCRIPT, akt.value, original_clause, dyn_str]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {LS_SCRIPT}: {e}")
    except FileNotFoundError:
        print(f"File {LS_SCRIPT} not found in the current directory.")


def main() -> None:
    set_english_locale()
    clear_console()
    print("\nThis program will help you identify the aktionsart of the main predicate in a clause.")

    while True:
        try:
            original = prompt_user(
                "\nPlease type a clause with the verb you want to test"
                "\nconjugated in the SIMPLE PAST (e.g., 'Peter ran home')."
                "\nIf it sounds very odd, type it in PRESENT (e.g., 'Mary knows English')."
                "\n\nClause: "
            )

            if not original:
                print("\nYou did not type any clause.")
                continue

            clause = original
            data = ClauseData()

            feats = obtain_features(clause, data)
            if feats is None:
                continue
            akt = determine_aktionsart(feats)
            if akt is None:
                restart_message()
                continue
            show_result(original, akt, feats)

            if not yes_no("\nDo you want to identify the aktionsart of another predicate? (y/n): "):
                time.sleep(1)
                return
            else:
                time.sleep(0.5)
                clear_console()

        except Exception as e:
            logging.error(f"\nUnexpected error: {e}")
            print("\nAn error occurred. Please, try again.")


if __name__ == "__main__":
    main()
