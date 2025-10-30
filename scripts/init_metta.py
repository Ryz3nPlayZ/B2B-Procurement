#!/usr/bin/env python3
"""
Initialize MeTTa Knowledge Base

Load and initialize MeTTa knowledge bases for the ASI system.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from metta.metta_engine import MeTTaEngine
from config.settings import settings


def setup_logging():
    """Setup logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('init_metta')


def load_knowledge_base_files(engine: MeTTaEngine, kb_path: str):
    """Load MeTTa knowledge base files."""
    logger = logging.getLogger('init_metta')
    
    kb_directory = Path(kb_path)
    if not kb_directory.exists():
        logger.error(f"Knowledge base directory not found: {kb_path}")
        return False
    
    # List of knowledge base files to load
    kb_files = [
        "buyer_policies.metta",
        "seller_a.metta", 
        "seller_b.metta",
        "seller_c.metta"
    ]
    
    success_count = 0
    for kb_file in kb_files:
        file_path = kb_directory / kb_file
        if file_path.exists():
            try:
                result = engine.load_knowledge_base(str(file_path))
                if result:
                    logger.info(f"Loaded knowledge base: {kb_file}")
                    success_count += 1
                else:
                    logger.error(f"Failed to load knowledge base: {kb_file}")
            except Exception as e:
                logger.error(f"Error loading {kb_file}: {e}")
        else:
            logger.warning(f"Knowledge base file not found: {kb_file}")
    
    logger.info(f"Successfully loaded {success_count}/{len(kb_files)} knowledge base files")
    return success_count > 0


def load_schema_files(engine: MeTTaEngine, schemas_path: str):
    """Load MeTTa schema files."""
    logger = logging.getLogger('init_metta')
    
    schemas_directory = Path(schemas_path)
    if not schemas_directory.exists():
        logger.error(f"Schemas directory not found: {schemas_path}")
        return False
    
    # List of schema files to load
    schema_files = [
        "core_types.metta",
        "buyer_schema.metta",
        "seller_schema.metta"
    ]
    
    success_count = 0
    for schema_file in schema_files:
        file_path = schemas_directory / schema_file
        if file_path.exists():
            try:
                result = engine.load_knowledge_base(str(file_path))
                if result:
                    logger.info(f"Loaded schema: {schema_file}")
                    success_count += 1
                else:
                    logger.error(f"Failed to load schema: {schema_file}")
            except Exception as e:
                logger.error(f"Error loading {schema_file}: {e}")
        else:
            logger.warning(f"Schema file not found: {schema_file}")
    
    logger.info(f"Successfully loaded {success_count}/{len(schema_files)} schema files")
    return success_count > 0


def test_metta_queries(engine: MeTTaEngine):
    """Test MeTTa queries to verify knowledge base is working."""
    logger = logging.getLogger('init_metta')
    
    # Test queries
    test_queries = [
        "procurement-policy",
        "budget-constraint", 
        "quality-requirement",
        "Inventory",
        "Pricing",
        "Product"
    ]
    
    success_count = 0
    for query_type in test_queries:
        try:
            # Simple test query
            query = f"(match &self ({query_type} $x $y) [({query_type} $x $y)])"
            result = engine.execute_query(query)
            
            if result is not None:
                logger.info(f"Query test passed: {query_type}")
                success_count += 1
            else:
                logger.warning(f"Query test returned None: {query_type}")
        except Exception as e:
            logger.error(f"Query test failed for {query_type}: {e}")
    
    logger.info(f"Query tests passed: {success_count}/{len(test_queries)}")
    return success_count > 0


def initialize_metta():
    """Initialize MeTTa knowledge base system."""
    logger = setup_logging()
    logger.info("Starting MeTTa knowledge base initialization")
    
    try:
        # Get configuration
        metta_config = settings.get_metta_config()
        kb_path = metta_config['knowledge_base_path']
        schemas_path = metta_config['schemas_path']
        
        logger.info(f"Knowledge base path: {kb_path}")
        logger.info(f"Schemas path: {schemas_path}")
        
        # Initialize MeTTa engine
        engine = MeTTaEngine(metta_config)
        logger.info("MeTTa engine initialized")
        
        # Load knowledge base files
        kb_success = load_knowledge_base_files(engine, kb_path)
        if not kb_success:
            logger.error("Failed to load knowledge base files")
            return False
        
        # Load schema files
        schema_success = load_schema_files(engine, schemas_path)
        if not schema_success:
            logger.error("Failed to load schema files")
            return False
        
        # Test queries
        query_success = test_metta_queries(engine)
        if not query_success:
            logger.warning("Some query tests failed, but continuing")
        
        # Get final status
        status = engine.get_knowledge_base_status()
        logger.info(f"MeTTa initialization complete: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"MeTTa initialization failed: {e}")
        return False


def main():
    """Main entry point for the script."""
    success = initialize_metta()
    
    if success:
        print("✅ MeTTa knowledge base initialization completed successfully")
        sys.exit(0)
    else:
        print("❌ MeTTa knowledge base initialization failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

