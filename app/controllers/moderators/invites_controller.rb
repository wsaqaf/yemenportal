class Moderators::InvitesController < ApplicationController
  before_action :authenticate_user!
  before_action :find_user

  def create
    @user.invite!
    redirect_to :back
  end

  private

  def find_user
    @user = User.find(params.fetch(:moderator_id))
  end
end
