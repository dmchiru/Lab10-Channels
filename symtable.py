"""
PA 4: The USILang Symbol Table -- starter.

Complete Environment and check_program below. See
PA_04_The_USILang_Symbol_Table.md, Part B, for the full requirements.
"""

from typing import Optional

from parser import Assignment, BinOp, Declaration, Number, Program, Variable


class SemanticError(Exception):
    pass


class Environment:
    def __init__(self, parent: Optional["Environment"] = None) -> None:
        self.parent = parent
        self._names: dict = {}  # name -> declaration line, THIS scope only

    def define(self, name: str, line: int) -> None:
        """
        Store name -> line in THIS scope. Raise SemanticError if `name`
        is already defined in THIS scope (not a parent scope --
        shadowing a parent name is allowed).
        """
        # TODO
        if name in self._names:
            original_line = self._names[name]
            raise SemanticError(
                f"Duplicate declaration of '{name}' "
                f"(line {line}; originally declared line {original_line})."
            )

        self._names[name] = line

    def resolve(self, name: str) -> int:
        """
        Look up `name` in this scope, then climb `parent` links.
        Return the declaration line, or raise SemanticError if not
        found anywhere in the chain.
        """
        if name in self._names:
            return self._names[name]

        if self.parent is not None:
            return self.parent.resolve(name)

        raise SemanticError(f"Use of undeclared variable '{name}'.")


def check_program(ast: Program) -> Environment:
    """
    Walk `ast.statements` in order, using one top-level Environment.
    For a Declaration: resolve every Variable in its expr BEFORE
    defining the new name (so `let x = x;` fails as use-before-decl).
    For an Assignment: resolve the assigned-to name, then resolve
    every Variable in its expr. Errors must surface at the first
    offending statement, not be collected and reported together.
    """
    env = Environment()

    def resolve_with_line(name: str, line: int) -> None:
        try:
            env.resolve(name)
        except SemanticError:
            raise SemanticError(
                f"Use of undeclared variable '{name}' (line {line})."
            )   

    def check_expr(expr) -> None:
        if isinstance(expr, Number):
            return

        if isinstance(expr, Variable):
            resolve_with_line(expr.name, expr.line)
            return

        if isinstance(expr, BinOp):
            check_expr(expr.left)
            check_expr(expr.right)
            return

    for stmt in ast.statements:
        if isinstance(stmt, Declaration):
            check_expr(stmt.expr)
            env.define(stmt.name, stmt.line)

        elif isinstance(stmt, Assignment):
            resolve_with_line(stmt.name, stmt.line)
            check_expr(stmt.expr)

    return env
