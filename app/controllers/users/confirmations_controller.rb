class Users::ConfirmationsController < Devise::ConfirmationsController
  def after_confirmation_path_for(_resource_name, resource)
    sign_in(resource)
    root_path
  end
end
