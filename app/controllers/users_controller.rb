class UsersController < ApplicationController
  before_action :authenticate_user!

  def index
    users = User.paginate(page: params[:page])
    render cell: true, model: users
  end

  def edit
    render cell: :form, model: current_user
  end

  def update
    current_user.attributes = user_params
    if current_user.save
      redirect_to root_path
    else
      render cell: :form, model: current_user
    end
  end

  private

  def user_params
    @_user_params ||= params.require(:user).permit(:first_name, :last_name, :email)
  end
end
