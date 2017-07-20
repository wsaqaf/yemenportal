class Users::AdminPermissionsController < ApplicationController
  def create
    authorize(user, :change_role?)
    user.update(role: User.role.admin)
    redirect_back(fallback_location: users_path)
  end

  def destroy
    authorize(user, :change_role?)
    user.update(role: User.role.member)
    redirect_back(fallback_location: users_path)
  end

  private

  def user
    @user ||= User.find(params[:user_id])
  end
end
