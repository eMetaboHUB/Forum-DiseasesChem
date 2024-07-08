// Ammonite 2.5.2, scala 2.13
// JAVA_OPTS="-Xmx16g -Xms16g" amm ....

import $ivy.`org.eclipse.rdf4j:rdf4j-storage:4.3.12`
import $cp.`ext-lib/Classyfire_file.jar`

import lib.ChemicalClassifier
import org.eclipse.rdf4j.model.impl.SimpleValueFactory
import org.eclipse.rdf4j.model.vocabulary.{DCTERMS, RDF, RDFS, VOID, XSD}
import org.eclipse.rdf4j.model.{Statement, ValueFactory}
import org.eclipse.rdf4j.query._
import org.eclipse.rdf4j.rio.{RDFFormat, Rio}

import java.io._
import java.nio.file.{Files, Path, Paths}
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.zip.{GZIPInputStream, GZIPOutputStream};

//object BuildChemOntForumGraph {
  def extractCID(input: String): Option[String] = {
    val cidPattern = "CID\\d+".r
    cidPattern.findFirstIn(input)
  }

  def extractNUMBER(input: String): Option[String] = {
    val cidPattern = "\\d+".r
    cidPattern.findFirstIn(input)
  }

@main 
def main(outputDir: String,relaseForum: String,pc_descr_canSMILES_value_files: os.Path*) = {

    val compound_prefix_name: String = "compound"
    val compound_prefix: String = "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"

    val chemont_prefix_name: String = "CHEMONTID" // !!! don't change this value. Depends results give by API Classiyfire.jar
    //val chemont_prefix : String = "http://classyfire.wishartlab.com/tax_nodes/C"
    val chemont_prefix: String = "http://purl.obolibrary.org/obo/CHEMONTID_"
    //NOTE OFI : FORUM v1 us -> http://purl.obolibrary.org/obo/CHEMONTID_

    val vf: ValueFactory = SimpleValueFactory.getInstance()

    var countSubjectDirectParent = 0
    var countTripleDirectParent = 0
    var countSubjectAltParent = 0
    var countTripleAltParent = 0

    def uncompressed(infile: String): InputStream = {
      new GZIPInputStream(new FileInputStream(new File(infile)))
    }

    def compressWithGzip(inputFile: String, outputFile: String): Unit = {
      val bufferSize = 1024
      val buffer = new Array[Byte](bufferSize)

      val fileInputStream = new FileInputStream(inputFile)
      val bufferedInputStream = new BufferedInputStream(fileInputStream, bufferSize)

      val fileOutputStream = new FileOutputStream(outputFile)
      val gzipOutputStream = new GZIPOutputStream(new BufferedOutputStream(fileOutputStream, bufferSize))

      try {
        Iterator
          .continually(bufferedInputStream.read(buffer))
          .takeWhile(_ != -1)
          .foreach(gzipOutputStream.write(buffer, 0, _))
      } finally {
        bufferedInputStream.close()
        gzipOutputStream.close()
      }
    }

    def createDirectoriesRecursively(path: Path): Unit = {

      if (!Files.exists(path)) {
        if (path.getParent != null)
          createDirectoriesRecursively(path.getParent)
        Files.createDirectory(path)
      }
    }

    def upload_Chemont_sh(): Unit = {
      
      val pWriter = new PrintWriter(new File(s"$outputDir/upload_Chemont.sh"))
 
      pWriter.write(
        s"""delete from DB.DBA.load_list ;
ld_dir_all ('./dumps/ClassyFire/direct-parent/$relaseForum/', '*.ttl.gz', 'https://forum.semantic-metabolomics.org/ClassyFire/direct-parent/$relaseForum');
ld_dir_all ('./dumps/ClassyFire/direct-parent/$relaseForum/', 'void.ttl', 'https://forum.semantic-metabolomics.org/ClassyFire/direct-parent/$relaseForum');
ld_dir_all ('./dumps/ClassyFire/alternative-parents/$relaseForum/', '*.ttl.gz', 'https://forum.semantic-metabolomics.org/ClassyFire/alternative-parents/$relaseForum');
ld_dir_all ('./dumps/ClassyFire/alternative-parents/$relaseForum/', 'void.ttl', 'https://forum.semantic-metabolomics.org/ClassyFire/alternative-parents/$relaseForum');
select * from DB.DBA.load_list;
rdf_loader_run();
checkpoint;
select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;
""")
      pWriter.close
    }

    def void(dirParent: String,
             countSubject: Int,
             countTriple: Int,
             title: String,
             description: String): Unit = {

      val fileWriter = new FileWriter(new File(s"$dirParent/void.ttl"))
      val writer = Rio.createWriter(RDFFormat.TURTLE, fileWriter)
      writer.startRDF()
      writer.handleNamespace(DCTERMS.PREFIX, DCTERMS.NAMESPACE)
      writer.handleNamespace(VOID.PREFIX, VOID.NAMESPACE)
      writer.handleNamespace(RDF.PREFIX, RDF.NAMESPACE)
      writer.handleNamespace(RDFS.PREFIX, RDFS.NAMESPACE)

      val graph = vf.createIRI(s"https://forum.semantic-metabolomics.org/ClassyFire/direct-parent/$relaseForum")
      writer.handleStatement(vf.createStatement(
        vf.createIRI("https://forum.semantic-metabolomics.org/ClassyFire/direct-parent"),
        DCTERMS.HAS_VERSION, graph))
      writer.handleStatement(vf.createStatement(graph, RDF.TYPE, VOID.LINKSET))

      val currentDate = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"))
      writer.handleStatement(vf.createStatement(graph, DCTERMS.CREATED, vf.createLiteral(currentDate, XSD.DATE)))
      writer.handleStatement(vf.createStatement(graph, DCTERMS.DESCRIPTION, vf.createLiteral(description)))
      writer.handleStatement(vf.createStatement(graph, DCTERMS.SOURCE, vf.createIRI("http://classyfire.wishartlab.com")))
      writer.handleStatement(vf.createStatement(graph, DCTERMS.TITLE, vf.createLiteral(title)))
      writer.handleStatement(vf.createStatement(graph, VOID.DISTINCT_SUBJECTS, vf.createLiteral(countSubject)))
      writer.handleStatement(vf.createStatement(graph, VOID.TRIPLES, vf.createLiteral(countTriple)))
      writer.handleStatement(vf.createStatement(graph, RDFS.SEEALSO,
        vf.createIRI("https://doi.org/10.1186/s13321-016-0174-y")))
      writer.endRDF()
      fileWriter.close()
    }

    val chemicalClassifier: ChemicalClassifier = new ChemicalClassifier()

    /* to avoid error read from reference */
    System.setProperty("org.eclipse.rdf4j.rio.verify_uri_syntax", "false")

    val dirDirParent = s"$outputDir/ClassyFire/direct-parent/$relaseForum/"
    val dirAltParent = s"$outputDir/ClassyFire/alternative-parents/$relaseForum/"

    createDirectoriesRecursively(Paths.get(dirDirParent))
    createDirectoriesRecursively(Paths.get(dirAltParent))

    pc_descr_canSMILES_value_files.foreach {
      case filePathP: os.Path =>
        val filePath = filePathP.toString
        println(s"---  $filePath --- ")
        // Manage input file format
        val is: InputStream = if (filePath.endsWith(".gz")) {
          println(" -- gunzip -- ")
          uncompressed(filePath)
        } else {
          new FileInputStream(filePath)
        }
        val numb = extractNUMBER(filePath) match {
          case Some(n) => n
          case None => (10000 + scala.util.Random.nextInt(10001)).toString
        }


        val output_dp = s"$dirDirParent/classyfire_direct_parent_$numb.ttl"
        val output_adp = s"$dirAltParent/classyfire_alternative_parent_$numb.ttl"

        println(s" -- $output_dp -- ")
        if (new File(output_dp).exists()) {
          new File(output_dp).delete()
        }
        val fileWriter_dp = new FileWriter(new File(output_dp))
        val writer_dp = Rio.createWriter(RDFFormat.TURTLE, fileWriter_dp)

        println(s" -- $output_adp -- ")

        if (new File(output_adp).exists()) {
          new File(output_adp).delete()
        }
        val fileWriter_adp = new FileWriter(new File(output_adp))
        val writer_adp = Rio.createWriter(RDFFormat.TURTLE, fileWriter_adp)

        writer_dp.startRDF()
        writer_dp.handleNamespace(compound_prefix_name, compound_prefix)
        //writer_dp.handleNamespace(chemont_prefix_name, chemont_prefix)
        writer_adp.startRDF()
        writer_adp.handleNamespace(compound_prefix_name, compound_prefix)
        //writer_adp.handleNamespace(chemont_prefix_name, chemont_prefix)

        val baseURI: String = new File(filePath).toURI.toString
        val format: RDFFormat = RDFFormat.TURTLE

        try {
          val res: GraphQueryResult = QueryResults.parseGraphBackground(is, baseURI, format, null)
          println(s"baseURI:$baseURI")
          try {
            while (res.hasNext) {
              try {
                val st: Statement = res.next()
                extractCID(st.getSubject.stringValue()) match {
                  case Some(cid) =>
                    val smiles = st.getObject.stringValue()
                    println(s"$cid,$smiles")

                    // ---------------------------------
                    // Classyfire API
                    // ---------------------------------
                    chemicalClassifier.classify(smiles)

                    // ---------------------------------
                    // DIRECT PARENT MANAGEMENT
                    // ---------------------------------
                    val dp = chemicalClassifier.taxonomic_classification.direct_parent
                      .split("\t")
                      .map(className => chemicalClassifier.ontology.node_hash.get(className).id)

                    countSubjectDirectParent += 1

                    dp.foreach(
                      chemontId => {
                        val chemont_id = chemontId.replace(chemont_prefix_name + ":", chemont_prefix)
                        val s = vf.createIRI(s"$compound_prefix$cid")
                        val o = vf.createIRI(chemont_id)
                        writer_dp.handleStatement(vf.createStatement(s, RDF.TYPE, o))
                        countTripleDirectParent += 1
                      })

                    // ---------------------------------
                    // ALT PARENT MANAGEMENT
                    // ---------------------------------

                    val ap = chemicalClassifier.alternative_parents.split("\t")
                      .map(className => chemicalClassifier.ontology.node_hash.get(className).id)

                    countSubjectAltParent += 1
                    ap.foreach(
                      chemontId => {
                        val chemont_uri = chemontId.replace(chemont_prefix_name + ":", chemont_prefix)
                        val s = vf.createIRI(s"$compound_prefix$cid")
                        val o = vf.createIRI(chemont_uri)
                        writer_adp.handleStatement(vf.createStatement(s, RDF.TYPE, o))
                        countTripleAltParent += 1
                      })

                  case None => println("Aucun identifiant CID trouvé")
                }

              } catch {
                case e: Exception =>
                  println(e.getLocalizedMessage)
                // Gérer l'erreur irrécupérable ici
              }

            }
          } catch {
            case e: Exception =>
              // Gérer l'erreur irrécupérable ici
              System.err.println("1:" + e.getMessage)
              System.exit(-1)
          } finally {
            writer_dp.endRDF()
            writer_adp.endRDF()

            fileWriter_dp.close()
            fileWriter_adp.close()

            res.close()

            compressWithGzip(output_dp, output_dp + ".gz")
            new File(output_dp).delete()
            compressWithGzip(output_adp, output_adp + ".gz")
            new File(output_adp).delete()

          }
        } catch {
          case e: Exception =>
            System.err.println("1:" + e.getMessage)
            System.exit(-1)
        } finally {
          void(dirDirParent,
            countSubjectDirectParent,
            countTripleDirectParent,
            "ChemOnt Classification - Direct parent",
            "This subset contains RDF triples providing links between " +
              "PubChem compounds and their class according to ChemOnt ontology from ClassyFire. " +
              "The provided class correspond to the Direct Parent, representing the dominant class in the molecule")
          void(dirAltParent,
            countSubjectAltParent,
            countTripleAltParent,
            "ChemOnt Classification - Alternative parents",
            "This subset contains RDF triples providing links between PubChem " +
              "compounds and their classes according to ChemOnt ontology from ClassyFire. " +
              "The provided classes correspond to the Alternative Parents, representing classes " +
              "describing the molecule but which not have an ancestor–descendant relationship with each " +
              "other or with the Direct Parent")
          
          upload_Chemont_sh()
          is.close()
        }
    }
  }
//}
