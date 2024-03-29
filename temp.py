## Imports
import os
import git


## Module Constants
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
EMPTY_TREE_SHA   = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

def diff_size(diff):
	"""
	Computes the size of the diff by comparing the size of the blobs.
	"""
	if diff.b_blob is None and diff.deleted_file:
		# This is a deletion, so return negative the size of the original.
		return diff.a_blob.size * -1

	if diff.a_blob is None and diff.new_file:
		# This is a new file, so return the size of the new value.
		return diff.b_blob.size

	# Otherwise just return the size a-b
	return diff.a_blob.size - diff.b_blob.size


def diff_type(diff):
	"""
	Determines the type of the diff by looking at the diff flags.
	"""
	if diff.renamed: return 'R'
	if diff.deleted_file: return 'D'
	if diff.new_file: return 'A'
	return 'M'

def versions(path):
	"""
	This function returns a generator which iterates through all commits of
	the repository located in the given path for the given branch. It yields
	file diff information to show a timeseries of file changes.
	"""
	# Create the repository, raises an error if it isn't one.
	repo = git.Repo(path)
	branch='master'
	# Iterate through every commit for the given branch in the repository
	for commit in repo.iter_commits(branch):
		# Determine the parent of the commit to diff against.
		# If no parent, this is the first commit, so use empty tree.
		# Then create a mapping of path to diff for each file changed.
		parent = commit.parents[0] if commit.parents else EMPTY_TREE_SHA
		diffs  = {
			diff.a_path: diff for diff in commit.diff(parent)
		}

		# The stats on the commit is a summary of all the changes for this
		# commit, we'll iterate through it to get the information we need.
		for objpath, stats in commit.stats.files.items():

			# Select the diff for the path in the stats
			diff = diffs.get(objpath)

			# If the path is not in the dictionary, it's because it was
			# renamed, so search through the b_paths for the current name.
			if not diff:
				for diff in diffs.values():
					if diff.b_path == path and diff.renamed:
						break

			# Update the stats with the additional information
			stats.update({
				'object': os.path.join(path, objpath),
				'commit': commit.hexsha,
				'author': commit.author.email,
				'timestamp': commit.authored_datetime.strftime(DATE_TIME_FORMAT),
				'size': diff_size(diff),
				'type': diff_type(diff),
			})
			# print stats
			for i in stats:
				print i,":",stats[i]
			print "----------"
			# yield stats

# if __name__ == "__main__":
	# path = 'GIT_REPO_PATH'

path = os.getenv('GIT_REPO_PATH')
versions(path)

