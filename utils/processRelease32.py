from collections import OrderedDict, namedtuple
import csv
import glob
import os
import re
import shutil

# URI patterns
# {registry}/BUFR4/{table}/[{tableNotation}]

headers = OrderedDict(
    (('((BUFR|CREX)_TableA)', '"CodeFigure","Meaning_en","Status"'),
     ('((BUFRCREX)_CodeFlag)_([0-9]{2})', ('FXY,ElementName_en,CodeFigure,'
                                           'EntryName_en,EntryName_sub1_en,'
                                           'EntryName_sub2_en,Note_en,Status')),
     ('((BUFRCREX)_TableB)_([0-9]{2})', ('ClassNo,ClassName_en,FXY,'
                                         'ElementName_en,'
                                         'Note_en,BUFR_Unit,BUFR_Scale,'
                                         'BUFR_ReferenceValue,'
                                         'BUFR_DataWidth_Bits,'
                                         'CREX_Unit,CREX_Scale,'
                                         'CREX_DataWidth_Char,Status')),
     ('((BUFR|CREX)_TableC)', ('"FXY","OperatorName_en",'
                               '"OperationDefinition_en","Note_en",'
                               '"Status"')),
     ('((BUFR|CREX)_TableD)_([0-9]{2})', ('Category,CategoryOfSequences_en,FXY1,'
                                          'Title_en,SubTitle_en,FXY2,'
                                          'ElementName_en,ElementDescription_en,'
                                          'Note_en,Status')))
    )

def check_substitution(astr):
    if '{' in astr or '}' in astr:
        raise ValueError('{ or } in output, pattern replace missed')


# For each table csv file 
for infile in glob.glob('../*.csv'):
    # parse
    tablename = infile.split('/')[1].rstrip('.csv').replace('_en', '')

    print(tablename)
    key, = [k for k in headers if re.match(k, tablename)]
    tname = namedtuple('tname', 'table bufrcrex notation')
    tablename_parts = re.match(key, tablename).groups()
    print(tablename_parts)

    with open(infile, 'r') as inf:
        inlines = inf.read().splitlines()
        if inlines[0] != headers[key]:
            raise ValueError('{} != {}'.format(inlines[0], headers[key]))
        
    ALine = namedtuple('ALine', headers[key].replace('"',''))
    tlines = []
    for line in csv.reader(inlines[1:]):
        aline = ALine(*line)
        tlines.append(aline)

    # Create a folder structure for the structured contents
    tpath = tablename_parts[0]
    if not os.path.exists(tpath):
        os.mkdir(tpath)
    tablenotations = False
    cspath = tpath
    csname = tpath
    if len(tablename_parts) == 3:
        tablenotations = True
        # then this has a list of identified tables
        id_path = os.path.join([tablename_parts[0],tablename_parts[2]])
        if not os.path.exists(id_path):
            os.mkdir(id_path)
        cspath = id_path
        csname = tablename_parts[2]

    # Create files, based on templates
    if tablenotations:
        with open('templates/regRegister.ttl', 'r') as reg:
            areg = reg.read()
            areg = areg.format(uri=tpath, label=tpath, description=tpath,
                               remainder='')
            with open('{}/register.ttl'.format(tpath), 'rw') as regfile:
                check_substitution(areg)
                regfile.write(areg)
    with open('templates/skosConceptScheme.ttl', 'r') as csch:
        aConceptScheme = csch.read()
        aConceptScheme = aConceptScheme.format(uri=csname, label=csname,
                                               description=csname,
                                               notation=csname, remainder='')
        with open('{}/conceptScheme.ttl'.format(cspath), 'rw') as csfile:
            check_substitution(aConceptScheme)
            csfile.write(aConceptScheme)
    for tline in tlines:
        with open('templates/skosConcept.ttl', 'r') as con:
            aConcept = con.read()
            # harcoded!!
            aConcept = aConcept.format(uri=tline., label=, description=,
                                       notation=, remainder='')
            with open('{}/{}.ttl'.format(cspath, ), 'rw')
    break

