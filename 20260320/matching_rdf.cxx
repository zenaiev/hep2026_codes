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
  std::vector<std::string> particles = {"el", "mu"};
  for (const auto& pat : particles) {
    auto rdf1 = rdf.Define("genSign_"+pat, []() { return 1; });
    rdf1 = rdf1.Define("match_"+pat, matching, {"genSign_"+pat, "mcLp", "N"+pat, pat+"Pt", pat+"Eta", pat+"Phi"});
    rdf1 = rdf1.Define("irec_best_"+pat, "match_"+pat+"[0]");
    rdf1 = rdf1.Define("delta_best_"+pat, "match_"+pat+"[1]");
    auto rdf2 = rdf1.Filter(TString::Format("delta_best_%s<0.1&&delta_best_%s>0.", pat.c_str(), pat.c_str()).Data());
    rdf2 = rdf2.Define(std::format("rec_pt_{}", pat), std::format("{}Pt[irec_best_{}]", pat, pat));
    rdf2 = rdf2.Define("gen_pt_"+pat, "TMath::Sqrt(mcLp[0]*mcLp[0]+mcLp[1]*mcLp[1])");
    rdf2.Snapshot("tree_matched_"+pat, "matching_rdf_"+pat+".root", {"irec_best_"+pat, "delta_best_"+pat, "rec_pt_"+pat, "gen_pt_"+pat});
  }
  return 0;
}
