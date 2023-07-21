#!/usr/bin/env python

__import__('pkg_resources').declare_namespace('emr')

import emr.encoding.LSystem

# """
# Genome/Phenotype individual encoding module
# """

# from .LSystem import GraphGrammar as grammar_encoding


# ENCODING_MAPPING = {'grammar': grammar_encoding}


# def get_encoding(toolbox, config):
#     """Load encoding"""
#     enc_type = config['encoding']['type']
#     if enc_type in ENCODING_MAPPING:
#         ENCODING_MAPPING[enc_type](toolbox, config)
#     else:
#         raise NotImplementedError(f"Encoding: '{enc_type}' not supported, available: {ENCODING_MAPPING.keys()}")