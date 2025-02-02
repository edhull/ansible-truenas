#!/usr/bin/python
__metaclass__ = type

# XXX - DOCUMENTATION docstring
DOCUMENTATION = r'''
---
module: service
short_descrption: Manage TrueNAS services
description:
  - Controls services on TrueNAS.
options:
  enabled:
    description:
      - Whether the service is enabled (True) or disabled (False)
    type: bool
  ha_propagate:
    description:
      - I don't know. I think this is for High Availability in
        TrueNAS Enterprise.
  name:
    description:
    - Name of the service.
    type: str
    required: true
  state:
    description:
      - "C(started)/C(stopped): make sure the service is started/stopped."
      - C(restarted) will unconditionally restart the service.
      - C(reloaded) will unconditionally reload the service.
      - At least one of C(state) and C(enabled) is reauired.
    type: str
    choices: [ started, stopped, restarted, reloaded ]
'''

# XXX - EXAMPLES string
EXAMPLES = '''
- name: Enable a service
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arensb.truenas.plugins.module_utils.middleware \
    import MiddleWare as MW


def main():
    def start_service(service):
        """Start the given service."""

        err = None
        try:
            err = mw.call("service.start",
                          service)
            # XXX - Add ha_propagate once it's supported
        except Exception as e:
            module.fail_json(msg=f"Error starting service {service}: {e.stderr}")
        return err

    def stop_service(service):
        """Stop the given service."""

        err = None
        try:
            err = mw.call("service.stop",
                          service)
            # XXX - Add ha_propagate once it's supported
        except Exception as e:
            module.fail_json(msg=f"Error stopping service {service}: {e.stderr}")
        return err

    def restart_service(service):
        """Restart the given service."""

        err = None
        try:
            err = mw.call("service.restart",
                          service)
            # XXX - Add ha_propagate once it's supported
        except Exception as e:
            module.fail_json(msg=f"Error restarting service {service}: {e.stderr}")
        return err

    def reload_service(service):
        "Reload the given service."

        err = None
        try:
            err = mw.call("service.reload",
                          service)
            # XXX - Add ha_propagate once it's supported
        except Exception as e:
            module.fail_json(msg=f"Error reloading service {service}: {e.stderr}")
        return err

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True, default=None),
            state=dict(type='str',
                       choices=['started', 'stopped', 'reloaded', 'restarted']),
            enabled=dict(type='bool'),
            ha_propagate=dict(type='bool')
        ),
        supports_check_mode=True,
        required_one_of=[['state', 'enabled']]
    )

    result = dict(
        changed=False,
        msg=''
    )

    mw = MW()

    # Get service name
    service = module.params['name']

    # Get information about the service
    try:
        # err = Midclt.call("service.query",
        #                   [["service", "=", service]])
        err = mw.call("service.query",
                      [["service", "=", service]])
    except Exception as e:
        # XXX - Should limit it to expected exceptions
        module.fail_json(msg=f"Error getting service {service} state: {e.stderr}")

    # If the service was found, 'err' should be an array of 1 entries.
    # If the service was not found, 'err' is an empty array: [].

    # XXX - Check that the service was found. What to do if it wasn't?

    # XXX - Do we want these? They're purely informational.
    result['service_id'] = err[0]['id']
    result['name'] = err[0]['service']
    result['enabled'] = err[0]['enable']
    result['state'] = err[0]['state']
    result['pids'] = err[0]['pids']

    # XXX - API:
    # - service.query
    # - service.reload (service)
    # - service.restart (service)
    # - service.start (service)
    # - service.started (service)

    want_state = module.params['state']

    # XXX - Check whether the state is correct.
    # midctl state can be "RUNNING", "STOPPED", "UNKNOWN".
    if want_state is not None:
        # XXX - Maybe abort on "UNKNOWN"?

        if want_state == "started":
            # XXX - Make sure service is running
            pass
        elif want_state == "stopped":
            # XXX - Make sure service is not running
            if result['state'] != "STOPPED":
                if module.check_mode:
                    pass
                else:
                    stop_service(result['name'])
        elif want_state == "restarted":
            # Unconditionally restart the service
            if module.check_mode:
                pass
            else:
                err = restart_service(result['name'])
            result['changed'] = True
            result['msg'] = "service restarted"

        elif want_state == "reloaded":
            # Unconditionally reload the service
            if module.check_mode:
                pass
            else:
                err = reload_service(result['name'])
            result['changed'] = True
            result['msg'] = "service reloaded"

    # XXX - Check whether the enabledness is correct.
    want_enabled = module.params['enabled']
    if want_enabled is not None:
        if result['enabled'] != want_enabled:
            # XXX - Enable or disable, as required.
            # call service.update, with "id", and "enable: true"
            # (I think)

            # midclt call service.update afp '{"enable": false}'
            pass

    # XXX - Set result['changed']

    module.exit_json(**result)


if __name__ == "__main__":
    main()
