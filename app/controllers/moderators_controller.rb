class ModeratorsController < ApplicationController
  before_action :find_user, only: [:destroy]

  def index
    moderators = User.moderators.paginate(page: params[:page], per_page: 20)
    render cell: true, model: moderators
  end

  def destroy
    @user.update(role: "MEMBER")
    redirect_to :back
  end

  private

  def find_user
    @user = User.find(params.fetch(:id))
  end
end