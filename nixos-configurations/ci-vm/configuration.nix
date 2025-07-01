{
  lib,
  modulesPath,
  pkgs,
  ...
}:

let

  inherit (lib.modules)
    mkMerge
    ;

in

{
  imports = [
    (modulesPath + "/profiles/qemu-guest.nix")
    (modulesPath + "/profiles/minimal.nix")
  ];

  config = mkMerge [

    {

      # Needed to make nix flake check happy
      system.stateVersion = "25.05";
      nixpkgs.hostPlatform = "x86_64-linux";
      fileSystems = {
        "/".device = "/dev/hda1";
      };

      boot.loader.systemd-boot.enable = true;
      boot.loader.efi.canTouchEfiVariables = true;

      # Configure networking
      networking.useDHCP = true;

      # Create user "test"
      users.users.test.isNormalUser = true;
      users.users.test.initialPassword = "test";
      users.users.test.extraGroups = [ "wheel" ];

      # Enable passwordless ‘sudo’ for the "test" user
      services.getty.autologinUser = "test";
      security.sudo.wheelNeedsPassword = false;

      # Make VM output to the terminal instead of a separate window
      virtualisation.vmVariant.virtualisation.graphics = false;

    }

    {
      # Setup environment for act
      environment.systemPackages = with pkgs; [
        act
        git
        vim
      ];
      virtualisation.docker.enable = true;
      virtualisation.vmVariant.virtualisation.diskSize = 8192;
      virtualisation.vmVariant.virtualisation.memorySize = 2048;
      virtualisation.vmVariant.virtualisation.cores = 4;
      users.users.test.extraGroups = [ "docker" ];
    }

  ];
}
