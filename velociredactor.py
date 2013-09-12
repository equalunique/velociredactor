#!/usr/bin/python
import os
import tempfile
import argparse
import subprocess
import xmlrpclib

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


#print("ipdf_abs: %s" % os.path.abspath(args.ipdf))
ipdf_abs = os.path.abspath(args.ipdf)
ipdf_bas = os.path.basename(ipdf_abs)
ipdf_dir = os.path.dirname(ipdf_abs)
if os.path.isfile(ipdf_abs):
    print("ipdf_abs: %s" % ipdf_abs)
    print("ipdf: %s" % os.path.basename(ipdf_abs))
else:
    print("invalid argument for ipdf: %s" % args.ipdf )

#print("tmpl_abs: %s" % os.path.abspath(args.tmpl))
tmpl_abs = os.path.abspath(args.tmpl)
tmpl_bas = os.path.basename(tmpl_abs)
if os.path.isfile(tmpl_abs):
    print("tmpl_abs: %s" % tmpl_abs)
    print("tmpl: %s" % os.path.basename(tmpl_abs))
else:
    print("invalid argument for tmpl: %s" % args.tmpl )

print("osfx: %s" % args.osfx)

nosp_ipdf_bas = ipdf_bas
nosp_ipdf_bas = nosp_ipdf_bas.replace(" ", "_")
nosp_ipdf_bas = nosp_ipdf_bas.replace(",","")
nosp_ipdf_bas = nosp_ipdf_bas.replace("(","")
nosp_ipdf_bas = nosp_ipdf_bas.replace(")","")
print("nosp_ipdf_bas: %s" % nosp_ipdf_bas)

nosp_ipdf_abs = ipdf_abs.replace(ipdf_bas, nosp_ipdf_bas)
print("nosp_ipdf_abs: %s" % nosp_ipdf_abs)
os.rename(ipdf_abs, nosp_ipdf_abs)

fileName, fileExtension = os.path.splitext(nosp_ipdf_bas)
print("fileName: %s" % fileName)
print("fileExtension: %s" % fileExtension)
print("gs thingy: %d")
tup = (fileName, "%d", "png")
pngt_bas = '.'.join(tup)

# Create Temp Directory
tdir = tempfile.mkdtemp()
#print tdir

os.chdir(tdir)

print("pngt_bas: %s" % pngt_bas)
print("nosp_ipdf_abs: %s" % nosp_ipdf_abs)
sub = ''.join([
	'gs'
	' -q',
	' -dNOPAUSE',
	' -dBATCH',
	' -sDEVICE=pngalpha',
	' -r300',
	' -dEPSCrop',
	' -sOutputFile=',
	pngt_bas,
	' ',
	nosp_ipdf_abs
])
print(sub)
subprocess.check_output([sub], shell=True)

png_file_list = []
print("Opened temporary directory: %s" % tdir)
png_file_list = sorted(os.listdir(tdir))
for png_file in png_file_list:
	print("Created %s" % png_file)

## Open GIMP without UI

#Connect to GIMP XML-RPC Server
s = xmlrpclib.ServerProxy('http://localhost:8000') 

#Load template
print s.load_template(tmpl_abs)

# For each PNG
for png_file in png_file_list:
	# Load PNG to libgimp
	print s.load_png('/'.join([tdir,png_file]))
	# Deskew PNGs via libgimp and deskew
	print s.apply_deskew()
	# Apply Redaction Template via libgimp
	if png_file == png_file_list[0]:
		print s.apply_redactions()
	# Save PNG
	print s.save_png()
	# Close PNG
	print s.close_png()

# Close template
print s.close_template()
# Quit GIMP
print s.quit_gimp()


# PNGs 2 PDFs via ImageMagick
i = 1
pdf_file_list = []
for png_file in png_file_list:
	pdf_file = '.'.join([
		fileName,
		str(i),
		'pdf'
	])
	sub = ''.join([
		'/usr/bin/convert ',
		png_file,
		' ',
		pdf_file
	])
	i = i + 1
	pdf_file_list.append(pdf_file)
	print(sub)
	subprocess.check_output([sub], shell=True)




# Consolidate PDFs via GhostScript

fileName, fileExtension = os.path.splitext(nosp_ipdf_bas)
opdf_bas = '.'.join([fileName, "redacted", 'pdf'])
opdf_abs = '/'.join([ipdf_dir, opdf_bas])
sub = ''.join([
	''.join([
		'gs'
		' -q',
		' -dNOPAUSE',
		' -dBATCH',
		' -dSAFER',
		' -sDEVICE=pdfwrite',
		' -sOutputFile=',
		opdf_abs,
		' ',
	]),
	' '.join(
		pdf_file_list
	)
])
print(sub)
subprocess.check_output([sub], shell=True)


# Clear Temp Directory
print("Cleaning temporary files in %s" % tdir)
for the_file in os.listdir(tdir):
	file_path = os.path.join(tdir, the_file)
	try:
		os.unlink(file_path)
		print("Deleted temporary file %s" % the_file)
	except Exception, e:
		print e
print("File deletions complete. Removing temporary directory.")
# Close Temp Directory
os.removedirs(tdir)
print("Deleted %s" % tdir)
