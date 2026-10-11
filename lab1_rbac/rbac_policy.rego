package runtime_shield.authz

default allow = false

# Allow access to public data for everyone
allow {
    input.action == "read_file"
    startswith(input.resource, "/public/")
}

# Allow access to executive data ONLY if the user has the 'admin' role
allow {
    input.action == "read_file"
    startswith(input.resource, "/executive/")
    "admin" == input.user.roles[_]
}
