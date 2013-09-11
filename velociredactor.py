#!/usr/bin/python
import argparse

parser = argparse.ArgumentParser(description='Redact info from PDF based on GIMP template')
#parser.add_argument('ipdf', required=True, help='PDF to perform redaction on')
parser.add_argument('--ipdf', help='PDF to perform redaction on', required=True)
#outGroup = parser.add_mutually_exclusive_group(required=True)
#outGroup = parser.add_mutually_exclusive_group()
#parser.add_argument('opdf', help='PDF to output to', required=True)
parser.add_argument('--osfx', help='Appendied suffix for redacted output PDF', required=True)
#parser.add_argument('tmpl', required=True, help='GIMP template for redaction')
parser.add_argument('--tmpl', help='GIMP template for redaction', required=True)
args = parser.parse_args()

print("ipdf: %s" % args.ipdf )
print("osfx: %s" % args.osfx )
print("tmpl: %s" % args.tmpl )
