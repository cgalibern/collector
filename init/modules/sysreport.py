import os
from subprocess import *
import copy
import uuid

class sysreport(object):
    def __init__(self):
        here_d = os.path.dirname(__file__)
        self.collect_d = os.path.join(here_d, '..', 'uploads', 'sysreport')
        self.cwd = os.getcwd()

    def timeline(self, nodes=[]):
        data = []
        for node in nodes:
            data += self._timeline(node)
        return data

    def _timeline(self, nodename):
        s = self.log(nodename)
        data = self.parse_log(s, nodename)
        if len(data) > 1:
            # do not to display the node sysreport initial commit
            data = data[:-1]
        return data

    def parse_log(self, s, nodename):
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
                fpath = line.split(" | ")[0].strip().strip('"')
                changed.add(fpath)
            data[i]['stat'] = sorted(changed)
            data[i]['group'] = nodename
        return data

    def log(self, nodename=None):
        git_d = os.path.join(self.collect_d, nodename, ".git")
        cmd = ["git", "--git-dir="+git_d, "log", "-n", "300",
               "--stat=510,500", "--date=iso"]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def show_data(self, cid, nodename):
        ss = self.show_stat(cid, nodename)
        s = self.show(cid, nodename)
        data = self.parse_show(s)
        data['stat'] = self.parse_show_stat(ss)
        return data

    def show(self, cid, nodename):
        git_d = os.path.join(self.collect_d, nodename, ".git")
        cmd = ["git", "--git-dir="+git_d, "show", '--pretty=format:%ci%n%b', cid]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def show_stat(self, cid, nodename):
        git_d = os.path.join(self.collect_d, nodename, ".git")
        cmd = ["git", "--git-dir="+git_d, "show", '--pretty=format:%ci%n%b', '--numstat', cid]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def parse_show_stat(self, s):
        lines = s.split("\n")
        data = {}
        for line in lines:
            try:
                insertions, deletions, fpath = line.split("\t")
                insertions = int(insertions)
                deletions = int(deletions)
            except:
                continue
            data[fpath] = (insertions, deletions)
        return data

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
        git_d = os.path.join(self.collect_d, nodename, ".git")
        cmd = ["git", "--git-dir="+git_d, "ls-tree", "-r", cid]
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
              "fpath": line.split("	")[-1].strip('"'),
            }
            data.append(d)
        return data

    def lstree_data(self, cid, nodename):
        s = self.lstree(cid, nodename)
        return self.parse_lstree(cid, s)

    def show_file(self, fpath, cid, _uuid, nodename):
        git_d = os.path.join(self.collect_d, nodename, ".git")
        cmd = ["git", "--git-dir="+git_d, "ls-tree", cid, fpath]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        try:
            validated_fpath = out[out.index("\t")+1:]
        except:
            validated_fpath = fpath

        cmd = ["git", "--git-dir="+git_d, "show", _uuid]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return {'fpath': validated_fpath, 'content': out}


if __name__ == "__main__":
    o = sysreport()
    #print(o.timeline(["x64lmwbiegt"]))
    print(o.lstree_data('f8f48a59d61501e290cb521641ff27bd747252cb', 'x64lmwbiegt'))
