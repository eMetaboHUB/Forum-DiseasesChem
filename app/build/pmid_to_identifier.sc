// Ammonite 2.5.2, scala 2.13
// JAVA_OPTS="-Xmx16g -Xms16g" amm app/build/pmid_to_identifier.sc pmid_identifiers.tsv data-test/pc_reference_identifier_000001.ttl.gz

import $ivy.`com.github.p2m2::discovery:0.4.3`

import java.io.{File, FileInputStream}
import java.nio.file.{Files, Paths}
import java.util.zip.GZIPInputStream
import scala.util.{Try,Success,Failure}

import scala.concurrent._
import scala.concurrent.duration._

import fr.inrae.metabohub.semantic_web.configuration._
import fr.inrae.metabohub.semantic_web.rdf._
import fr.inrae.metabohub.semantic_web._
import java.io._

def uncompressed(outputName: String, infile: String): Unit = {
  val inputStream = new GZIPInputStream(new FileInputStream(new File(infile)))
  Files.copy(inputStream, Paths.get(outputName))
}


@main
def main(outfile : String, pc_reference_identifier_files : String*) : Unit = {


    if (new File(outfile).exists()) {
      System.err.println(s"$outfile exists !")
      System.exit(-1)
    }

    /* to avoid error read from reference */
    System.setProperty("org.eclipse.rdf4j.rio.verify_uri_syntax","false")

    val fileWriter = new FileWriter(new File(outfile))

    pc_reference_identifier_files.foreach  {
        case (filePath : String) => {
            println(s"---  $filePath --- ")
            val path : String = if (filePath.endsWith(".gz")) {
              println(" -- gunzip -- ")
              val p = filePath.replace(".gz","")
              uncompressed(p,filePath)
              p
            } else {
              filePath
            }
            val config : SWDiscoveryConfiguration =
                    SWDiscoveryConfiguration
                    .init()
                    .localFile(
                        filename = path,
                        mimetype = "text/turtle"
                    );

            val r = Await.result(SWDiscovery(config)
                .prefix("dcterms","http://purl.org/dc/terms/")
                .something("pmid")
                 .isSubjectOf(URI("dcterms:identifier"),"identifier")
                 .filter.contains("pubmed.ncbi.nlm.nih")
                  .filter.not.contains("PMC")
                .select(Seq("pmid","identifier"))
                .commit()
                .raw, 100.minutes)
              
              
              r("results")("bindings")
              .arr
              .map(res => 
                (
                  res("pmid")("value").str.split("/").last,
                  res("identifier")("value").str.split("/").last)
                ).foreach {
                  case (pmid,identifier) => fileWriter.write(s"$pmid\t$identifier\n")
                }

              if (filePath.endsWith(".gz")) {
                new File(path).delete()
              }
        }

    }
    fileWriter.close()
}
