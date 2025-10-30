# metta/metta_engine.py

import logging
import os
from typing import Any, List
import asyncio
from hyperon import MeTTa, ExpressionAtom, GroundedAtom

logger = logging.getLogger(__name__)

class MeTTaEngine:
    """
    Robust wrapper for the Hyperon MeTTa runtime with proper space management.
    """
    
    def __init__(self):
        self.metta = MeTTa()
        logger.info("Real Hyperon MeTTaEngine initialized.")

    async def load_metta_file(self, file_path: str):
        """
        Loads a .metta file by reading and parsing each expression.
        """
        def _load_sync():
            try:
                abs_path = os.path.abspath(file_path)
                if not os.path.exists(abs_path):
                    logger.error(f"MeTTa file not found at: {abs_path}")
                    return False
                
                # Read entire file content
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse and load all expressions at once
                result = self.metta.run(content)
                
                logger.info(f"Successfully loaded MeTTa file: {abs_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to load MeTTa file {file_path}: {e}")
                return False

        return await asyncio.to_thread(_load_sync)

    async def execute_query(self, query_str: str) -> List[Any]:
        """
        Executes a MeTTa query and converts results to Python objects.
        """
        def _execute_sync():
            try:
                results_from_hyperon = self.metta.run(query_str)
                
                if not results_from_hyperon:
                    logger.debug(f"Query '{query_str}' returned empty results")
                    return []

                # Flatten results - Hyperon returns List[List[Atom]]
                final_results = []
                for result_set in results_from_hyperon:
                    for atom in result_set:
                        py_result = self._atom_to_python(atom)
                        final_results.append(py_result)
                
                logger.debug(f"Query returned {len(final_results)} results")
                return final_results
            except Exception as e:
                logger.error(f"Query execution failed for '{query_str}': {e}")
                return []

        return await asyncio.to_thread(_execute_sync)

    def _atom_to_python(self, atom) -> Any:
        """
        Recursively converts Hyperon Atom to Python object.
        """
        # Handle ExpressionAtom (lists/tuples)
        if isinstance(atom, ExpressionAtom):
            return [self._atom_to_python(child) for child in atom.get_children()]
        
        # Handle GroundedAtom (wrapped values)
        if isinstance(atom, GroundedAtom):
            return atom.get_object()
        
        # Handle other atoms (Symbol, Variable, etc.) as strings
        atom_str = str(atom)
        
        # Try to convert to number
        try:
            if '.' in atom_str:
                return float(atom_str)
            return int(atom_str)
        except ValueError:
            return atom_str