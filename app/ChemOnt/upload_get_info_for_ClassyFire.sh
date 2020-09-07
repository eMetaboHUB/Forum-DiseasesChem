delete from DB.DBA.load_list ;
ld_dir_all ('./dumps/PubChem_InchiKey/inchikey/2020-06-10/', '*.ttl.gz', 'http://database/ressources/PubChem/inchikey/2020-06-10');
ld_dir_all ('./dumps/PubChem_InchiKey/inchikey/2020-06-10/', 'void.ttl', 'http://database/ressources/PubChem/inchikey/2020-06-10');
ld_dir_all ('./dumps/PMID_CID/2020-05-29/', '*.trig.gz', '');
ld_dir_all ('./dumps/PMID_CID/2020-05-29/', 'void.ttl', 'http://database/ressources/PMID_CID/2020-05-29');
select * from DB.DBA.load_list;
rdf_loader_run();
checkpoint;
select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;
