function _diff_len_not_equal(sh, lg, ds) {
  for (const [n, c] of [...lg].entries()) {
    if (c != sh[n])
      return [n, n + ds]
  }
}

function _diff_len_equal(un, deux) {
  let start = -1
  for (const [n, c] of [...deux].entries()) {
    if (c != un[n]) {
      if (start < 0)
        start = n
    } else {
      if (start >= 0)
        return [start, n]
    }
  }
  return [start, un.length]
}

export function diff(lhs, rhs) {
  let ds = lhs.length - rhs.length;
  let lg;
  let sh;
  if (lhs === rhs) {
    return [-1, -1];
  } else if (ds < 0) {
    lg = rhs;
    sh = lhs;
  } else {
    lg = lhs;
    sh = rhs;
  }
  ds = Math.abs(ds);
  let llg = lg.length;
  let lsh = sh.length;
  if (llg != lsh) {
    if (lg.startsWith(sh))
      return [llg - ds, llg];
    else
      return _diff_len_not_equal(sh, lg, ds);
  } else {
    return _diff_len_equal(lhs, rhs);
  }
}