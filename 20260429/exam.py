import ROOT
import array
import tqdm
import numpy as np
import unittest

# enable TTree branch
def add_branch(t, branch_name, branch_type, branch_size=1):
  br = array.array(branch_type, [0]*branch_size)
  t.SetBranchStatus(branch_name, 1)
  t.SetBranchAddress(branch_name, br)
  return br

# plot results, compute chi2 and p-value
def make_results(h_restored, h_gen, label):
  ROOT.gStyle.SetOptStat(0)
  c = ROOT.TCanvas(f'c_{label}', f'c_{label}', 600, 600)
  c.Divide(1, 3)
  c.cd(1)
  h_gen.SetLineColor(2)
  h_gen.GetXaxis().SetTitle('MET [GeV]')
  h_gen.GetYaxis().SetTitle('Events')
  h_restored.SetLineColor(4)
  ROOT.gPad.SetLogy()
  h_gen.Draw('e1p')
  h_restored.Draw('e1p same')
  leg = ROOT.TLegend(0.75, 0.75, 0.89, 0.89)
  leg.AddEntry(h_gen, 'true', 'lep')
  leg.AddEntry(h_restored, 'restored', 'lep')
  leg.Draw()
  c.cd(2)
  h_gen_over_gen = h_gen.Clone()
  h_gen_over_gen.GetYaxis().SetTitle('Ratio')
  h_gen_over_gen.Divide(h_gen)
  h_unf_over_gen = h_restored.Clone()
  h_unf_over_gen.Divide(h_gen)
  h_gen_over_gen.SetMinimum(0.5)
  h_gen_over_gen.SetMaximum(1.5)
  h_gen_over_gen.Draw('e1p')
  h_unf_over_gen.Draw('e1p same')
  c.cd(3)
  h_gen_over_gen_2 = h_gen_over_gen.Clone()
  h_gen_over_gen_2.SetMinimum(0.95)
  h_gen_over_gen_2.SetMaximum(1.05)
  h_gen_over_gen_2.Draw('e1p')
  h_unf_over_gen.Draw('e1p same')
  c.SaveAs(f'{label}.png')
  c.SaveAs(f'{label}.pdf')
  chi2 = sum((h_restored.GetBinContent(i+1)-h_gen.GetBinContent(i+1))**2/(h_restored.GetBinError(i+1)**2+h_gen.GetBinError(i+1)**2) for i in range(h_gen.GetNbinsX()))
  chi2_per_dof = chi2 / h_gen.GetNbinsX()
  p = ROOT.TMath.Prob(chi2,h_gen.GetNbinsX())
  print(f'{label} chi2_per_dof = {chi2:.2f}/{h_gen.GetNbinsX()} = {chi2_per_dof:.2f}, p = {p}')
  return p

def invert(h_resp, h_rec):
  nx = h_resp.GetNbinsX()  # rec
  ny = h_resp.GetNbinsY()  # gen
  R = np.zeros((nx, ny))
  for i in range(nx):
    for j in range(ny):
      R[i, j] = h_resp.GetBinContent(i+1, j+1)
  for j in range(ny):
    s = np.sum(R[:, j])
    if s > 0:
      R[:, j] /= s
  Rinv = np.linalg.inv(R)
  v_rec = np.array([h_rec.GetBinContent(i+1) for i in range(nx)])
  v_gen = np.matmul(Rinv, v_rec)
  h_unfold = h_met_gen.Clone("h_unfold")
  h_unfold.Reset()
  for i in range(ny):
    h_unfold.SetBinContent(i+1, v_gen[i])
  return h_unfold

# here implement unfolding (or any algorithm to restore rec -> gen distribution)
# you can pass extra arguments (responce matrix etc.)
def magic(h_rec):
  return h_rec


class TestUnfolding(unittest.TestCase):
  def test_pvalue(self):
    # this file should be used for responce matrix
    fname1 = 'ntuples-mc/TTJets_TuneZ2_7TeV-madgraph-tauola/00000/ttbarSel_merged.root'
    # this file should be used fore actual comparison (like data)
    fname2 = 'ntuples-mc/TTJets_TuneZ2_7TeV-madgraph-tauola/00001/ttbarSel_merged.root'
    # download these ROOT files from here (~ 1 GB):
    # https://cernbox.cern.ch/s/UmbXF1XxVrT4whQ

    # do something with fname1 here (responce matrix...)

    # now process fname2
    t2 = ROOT.TChain('tree')
    t2.Add(fname2)
    t2.SetBranchStatus('*', 0)
    mcNu = add_branch(t2, 'mcNu', 'f', 4)
    mcNubar = add_branch(t2, 'mcNubar', 'f', 4)
    metPx = add_branch(t2, 'metPx', 'f', 1)
    metPy = add_branch(t2, 'metPy', 'f', 1)
    nevents2 = t2.GetEntries()
    print(f'nevents2 = {nevents2}')
    h_met_rec = ROOT.TH1D('h_met_rec', 'h_met_rec', 5, 0., 500.)
    h_met_rec.Sumw2()
    h_met_gen = ROOT.TH1D('h_met_gen', 'h_met_gen', 5, 0., 500.)
    h_met_gen.Sumw2()
    for i in tqdm.tqdm(range(nevents2)):
      t2.GetEntry(i)
      met_rec = np.sqrt((mcNu[0]+mcNubar[0])**2+(mcNu[1]+mcNubar[1])**2)
      met_gen = np.sqrt(metPx[0]**2+metPy[0]**2)
      h_met_gen.Fill(met_gen)
      h_met_rec.Fill(met_rec)

    h_restored = magic(h_met_rec)
    # test passes if uncomment below
    #h_restored = h_met_gen
    p = make_results(h_restored, h_met_gen, 'met')
    self.assertTrue((p > 1e-3), msg = 'FAILED')


if __name__ == '__main__':
  unittest.main()
