function pip-install-save {
  pip install $1 || return 1
  if [ -z $(pip freeze | grep $1) ];
  then
    echo "Unable to save package $1 to requirements.txt because it was installed under a different name. Run 'pip freeze' to inspect installed packages."
    return 1
  fi
  echo $1 >> requirements.txt
}
