import sys
import random
from collections import deque

PRIME_CONSTANTS = [
    [3, 5, 7],
    [11, 13, 17],
    [19, 23, 29],
    [31, 37, 41],
    [43, 47, 53],
    [59, 61, 67],
    [71, 73, 79],
    [83, 89, 97],
    [101, 103, 107],
]

HELP_MSG = "Usage: python sacred_geometry.py <num_dice> <spell_level>"

class Solver:
    def __init__(self, dierolls, target):
        self.count = len(dierolls)
        self.dierolls = dierolls
        self.target_decoded = target
        self.target_encoded = (target << self.count) | ((1 << self.count) - 1)
        self.built_exprs = {}
        self.queue = deque()

    def encode_expr(self, value, numbers):
        return (value << self.count) | numbers

    def solve(self):
        # 初始化骰子表达式
        for i in range(self.count):
            encoded = self.encode_expr(self.dierolls[i], 1 << i)
            self.built_exprs[encoded] = ('die', self.dierolls[i])
            self.queue.append(encoded)

        while self.queue and self.target_encoded not in self.built_exprs:
            lhs = self.queue.popleft()
            lv = lhs >> self.count
            ln = lhs & ((1 << self.count) - 1)

            # 遍历所有可能的右操作数
            for rhs in list(self.built_exprs.keys()):
                rv = rhs >> self.count
                rn = rhs & ((1 << self.count) - 1)

                if (ln & rn) != 0:
                    continue  # 避免重复使用骰子

                # 尝试所有运算符组合
                for op in ['+', '-', '-rev', '*', '/', '/rev']:
                    nv = None
                    if op == '+':
                        nv = lv + rv
                    elif op == '-':
                        if lv >= rv:
                            nv = lv - rv
                    elif op == '-rev':
                        if rv >= lv:
                            nv = rv - lv
                    elif op == '*':
                        nv = lv * rv
                    elif op == '/':
                        if rv != 0 and lv % rv == 0:
                            nv = lv // rv
                    elif op == '/rev':
                        if lv != 0 and rv % lv == 0:
                            nv = rv // lv

                    if nv is None:
                        continue

                    nn = ln | rn
                    new_enc = self.encode_expr(nv, nn)

                    if new_enc not in self.built_exprs:
                        self.built_exprs[new_enc] = ('expr', lhs, op, rhs)
                        self.queue.append(new_enc)

        return self.target_encoded in self.built_exprs

    def print_solution(self):
        def build_expr(enc):
            expr = self.built_exprs[enc]
            if expr[0] == 'die':
                return str(expr[1])
            _, l, op, r = expr
            l_str = build_expr(l)
            r_str = build_expr(r)
            if op == '-rev':
                return f"({build_expr(r)} - {l_str})"
            if op == '/rev':
                return f"({build_expr(r)} / {l_str})"
            return f"({l_str} {op} {r_str})"

        expr_str = build_expr(self.target_encoded).replace('*', '×').replace('/', '÷')
        print(f"{self.target_decoded} = {expr_str[1:-1]}")

def main():
    if len(sys.argv) != 3:
        print(HELP_MSG)
        return

    try:
        num_dice = int(sys.argv[1])
        spell_level = int(sys.argv[2])
    except ValueError:
        print("Invalid input: please provide integers for num_dice and spell_level")
        return

    if not (1 <= num_dice <= 24):
        print("Number of dice must be between 1 and 24")
        return

    if not (1 <= spell_level <= 9):
        print("Spell level must be between 1 and 9")
        return

    dice = [random.randint(1, 6) for _ in range(num_dice)]
    print(f"Die rolls: {dice}")

    for target in PRIME_CONSTANTS[spell_level - 1]:
        solver = Solver(dice, target)
        if solver.solve():
            solver.print_solution()
            return

    print("No valid solution found for any target prime")

if __name__ == "__main__":
    main()
