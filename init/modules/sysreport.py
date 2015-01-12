import os
from subprocess import *
import copy
import uuid

class sysreport(object):
    def __init__(self):
        here_d = os.path.dirname(__file__)
        self.collect_d = os.path.join(here_d, '..', 'uploads', 'sysreport')
        self.git_d = os.path.join(self.collect_d, ".git")
        self.cwd = os.getcwd()

    def timeline(self, nodes=[]):
        data = []
        for node in nodes:
            data += self._timeline(node)
        return data

    def _timeline(self, nodename):
        s = self.log(nodename)
        data = self.parse_log(s)
        if len(data) > 1:
            # do not to display the node sysreport initial commit
            data = data[:-1]
        return data

    def parse_log(self, s):
        data = []
        d0 = {
         'id': '',
         'cid': '',
         'start': '',
         'stat': ''
        }
        d = copy.copy(d0)

        for line in s.split('\n'):
            if line.startswith("commit"):
                if d['start'] != '':
                    data.append(d)
                    d = copy.copy(d0)
                d['cid'] = line.split()[1]
                d['id'] = uuid.uuid1().hex
            elif line.startswith("Author:"):
                pass
            elif line.startswith("Date:"):
                l = line.split()
                d['start'] = "T".join(l[1:3])
            elif d['cid'] != '' and d['start'] != '':
                d['stat'] += line+'\n'
        if d['start'] != '':
            data.append(d)

        for i, d in enumerate(data):
            changed = set([])
            for line in d['stat'].split('\n'):
                if "files changed" in line:
                    d['summary'] = line.strip()
                    continue
                if " | " not in line:
                    continue
                fpath = line.split(" | ")[0].strip()
                changed.add(fpath)
            data[i]['stat'] = sorted(changed)
            data[i]['group'] = fpath.split('/')[0]
        return data

    def log(self, nodename=None):
        os.environ["COLUMNS"] = "500"
        cmd = ["git", "--git-dir="+self.git_d, "log", "-n", "300", "--stat", "--stat-name-width=500", "--date=iso"]
        if nodename is not None:
            cmd += ['--', nodename]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def show_data(self, cid, nodename):
        s = self.show(cid, nodename)
        return self.parse_show(s)

    def show(self, cid, nodename):
        cmd = ["git", "--git-dir="+self.git_d, "show", '--pretty=format:%ci%n%b', cid, '--', nodename]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def parse_show(self, s):
        lines = s.split("\n")
        if len(lines) > 0:
            date = lines[0]
            lines = lines[1:]
        else:
            date = ''
        d = {}
        block = []
        fpath = ''
        for line in lines:
            if line.startswith("diff "):
                if fpath != "" and len(block) > 0:
                    d[fpath] = '\n'.join(block)
                    block = []
                    fpath = ""
                continue
            if line.startswith("index "):
                continue
            if line.startswith("--- "):
                if "/dev/null" not in line:
                    fpath = line.replace("--- ", "").lstrip("a/")
                continue
            if line.startswith("+++ "):
                if "/dev/null" not in line:
                    fpath = line.replace("+++ ", "").lstrip("b/")
                continue
            block.append(line)
        if fpath != "" and len(block) > 0:
            d[fpath] = '\n'.join(block)
        return {'date': date, 'blocks': d}

    def lstree(self, cid, nodename):
        cmd = ["git", "--git-dir="+self.git_d, "ls-tree", "-r", cid, nodename]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def parse_lstree(self, cid, s):
        data = []
        for line in s.split('\n'):
            l = line.split()
            if len(l) < 4:
                continue
            d = {
              "cid": cid,
              "mode": l[0],
              "type": l[1],
              "oid": l[2],
              "fpath": line.split("	")[-1],
            }
            data.append(d)
        return data

    def lstree_data(self, cid, nodename):
        s = self.lstree(cid, nodename)
        return self.parse_lstree(cid, s)

    def show_file(self, fpath, cid, _uuid):
        cmd = ["git", "--git-dir="+self.git_d, "ls-tree", cid, fpath]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        validated_fpath = out[out.index(" ")+1:]

        cmd = ["git", "--git-dir="+self.git_d, "show", _uuid]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return {'fpath': validated_fpath, 'content': out}


if __name__ == "__main__":
    o = sysreport()
    #print(o.timeline(["clementine", "foo"]))
    print(o.show_data("50fa58c0d7bda6afcb27aaab3b3efa79390c067a", "foo"))
