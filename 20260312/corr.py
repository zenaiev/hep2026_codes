import ROOT
import argparse

def compute_correlation(rdf, variables, flag_graphs):
  means = [0 for _ in variables]
  covs = [[0. for _ in variables] for __ in variables]
  cors = [[0. for _ in variables] for __ in variables]
  graphs = {}
  residuals = {}

  for ivar,_ in enumerate(variables):
    rdf = rdf.Define(f'var_{ivar}', variables[ivar])
    means[ivar] = rdf.Mean(f'var_{ivar}')
    for ivar2 in range(ivar+1):
      rdf_tmp = rdf.Define(f'var2_{ivar2}', variables[ivar2])
      covs[ivar][ivar2] = rdf_tmp.Define('TMP', f'var_{ivar}*var2_{ivar2}').Mean('TMP')
      if flag_graphs and ivar != ivar2:
        graphs[f'var{ivar}_var{ivar2}'] = rdf_tmp.Graph(f'var_{ivar}', f'var2_{ivar2}')
        residuals[f'var{ivar}_var{ivar2}'] = rdf_tmp.Define('TMP', f'var_{ivar}-var2_{ivar2}').Histo1D('TMP')

  for ivar,var in enumerate(variables):
    means[ivar] = means[ivar].GetValue()
    for ivar2 in range(ivar+1):
      covs[ivar][ivar2] = covs[ivar][ivar2].GetValue()
      if flag_graphs and ivar != ivar2:
        graphs[f'var{ivar}_var{ivar2}'] = graphs[f'var{ivar}_var{ivar2}'].GetValue()
        residuals[f'var{ivar}_var{ivar2}'] = residuals[f'var{ivar}_var{ivar2}'].GetValue()

  for ivar,var in enumerate(variables):
    for ivar2 in range(ivar+1):
      num = covs[ivar][ivar2] - means[ivar] * means[ivar2]
      den = ((covs[ivar][ivar] - means[ivar]**2) * (covs[ivar2][ivar2] - means[ivar2]**2))**0.5
      cors[ivar][ivar2] = num / den
      if ivar != ivar2:
        covs[ivar2][ivar] = covs[ivar][ivar2]
        cors[ivar2][ivar] = cors[ivar][ivar2]
  #print(covs)
  #print(cors)
  rdf.Snapshot('corr', 'corr.root')
  return covs, cors, graphs, residuals

def print_matrix(variables, cors):
  offset = max(len(v) for v in variables) + 1
  print(' '*offset, end='')
  #print('\t\t', end='')
  for var in variables:
    #print(f'{var:{offset}s}', end='')
    print(f'{var:>{offset}s}', end='')
  print()
  for ivar in range(len(variables)):
    print(f'{variables[ivar]:{offset}s}', end='')
    for ivar2 in range(len(variables)):
      print(f'{cors[ivar][ivar2]:+{offset}.2f}' if abs(cors[ivar][ivar2]) > 0.05 else f'{"":{offset}s}', end='')
        
    print()
  

# compute correlation between gen and rec level for nu+nubar
# python corr.py -n mcNu[0]+mcNubar[0],metPx,mcNu[1]+mcNubar[1],metPy
# python corr.py -i matching.root -t tree_matched_el -n gen_pt_el,rec_pt_el -g
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Compute correlations")
  parser.add_argument("--names", "-n", type=str, required=True, help="variables (comma separated)")
  parser.add_argument("--input_file", "-i", type=str, default='ttbarSel_merged.root', help="input ROOT file")
  parser.add_argument("--tree_name", "-t", type=str, default='tree', help="TTree name")
  parser.add_argument("--nrepeat", type=int, default=1, help="number of files")
  parser.add_argument("--graphs", '-g', action='store_true', help="draw graphs")
  args = parser.parse_args()

  ROOT.EnableImplicitMT() # parallel
  rdf = ROOT.RDataFrame(args.tree_name, [args.input_file]*args.nrepeat)
  variables = args.names.split(',')

  covs, cors, graphs, residuals = compute_correlation(rdf, variables, args.graphs)
  print(residuals)
  print_matrix(variables, cors)

  for icollection, collection in enumerate([graphs, residuals]):
    for k in collection:
      c = ROOT.TCanvas()
      c.cd()
      if icollection == 0:
        prefix = 'g_'
        collection[k].Draw('ap')
      elif icollection == 1:
        prefix = 'h_'
        collection[k].Fit('gaus')
        collection[k].Draw()
      for ext in ['pdf', 'png']:
        c.SaveAs(f'{prefix}{k}.{ext}')

  print(f'number of runs: rdf = {rdf.GetNRuns()}') # should be 1
