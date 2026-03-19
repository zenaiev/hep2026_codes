#include <ROOT/RDataFrame.hxx> 
#include <ROOT/RVec.hxx> 
#include <Math/Vector4D.h> 
#include <TMath.h> 
#include <cmath> 
#include <Math/Vector4D.h>

ROOT::RVec<float> matching(const int genSign, const ROOT::RVec<float>& genp4, const int recN, const ROOT::RVec<float>& recPt, const ROOT::RVec<float>& recEta, const ROOT::RVec<float>& recPhi) {
  float delta_best = -1.0;
  int irec_best = -1;
  for (int irec = 0; irec < recN; irec++) {
    if (genSign * recPt[irec] < 0) {
      continue;
    }
    ROOT::Math::PxPyPzMVector genVector(genp4[0], genp4[1], genp4[2], genp4[3]);
    auto delta_phi = genVector.Phi()-recPhi[irec];
    if(delta_phi > TMath::Pi()) {
      delta_phi = 2 * TMath::Pi() - delta_phi;
    }
    auto delta2 = TMath::Power((genVector.Eta()-recEta[irec]), 2.) + TMath::Power(delta_phi, 2.);
    auto delta = TMath::Sqrt(delta2 >= 0. ? delta2 : 0.);
    if (delta_best < 0 || delta < delta_best) {
      delta_best = delta;
      irec_best = irec;
    }
  }
  ROOT::RVec<float> result = {float(irec_best), delta_best};
  return result;
}



// g++ matching_rdf.cxx -o matching_rdf `root-config --cflags --libs`
int main(int argc, char** argv) {
  int nrepeat = 1;
  std::string fname = "ttbarSel_merged.root"; // 7980 events, signal ttbar MC

  ROOT::RDataFrame rdf = ROOT::RDataFrame("tree", fname);
  auto rdf1 = rdf.Define("genSign_el", []() { return 1; });
  rdf1 = rdf1.Define("match_el", matching, {"genSign_el", "mcLp", "Nel", "elPt", "elEta", "elPhi"});
  rdf1 = rdf1.Define("irec_best_el", "match_el[0]");
  rdf1 = rdf1.Define("delta_best_el", "match_el[1]");
  auto rdf2 = rdf1.Filter("delta_best_el<0.1&&delta_best_el>0.");
  rdf2 = rdf2.Define("rec_pt_el", "elPt[irec_best_el]");
  rdf2 = rdf2.Define("gen_pt_el", "TMath::Sqrt(mcLp[0]*mcLp[0]+mcLp[1]*mcLp[1])");
  rdf2.Snapshot("tree_matched_el", "matching_rdf.root", {"irec_best_el", "delta_best_el", "rec_pt_el", "gen_pt_el"});

  return 0;
}
