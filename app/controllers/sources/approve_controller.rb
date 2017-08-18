class Sources::ApproveController < ApplicationController
  before_action :authenticate_user!, :check_permissions
  before_action :find_source

  def update
    @source.update(approve_state: Source.approve_state.approved)
    redirect_to :back
  end

  private

  def find_source
    @source = Source.not_deleted.find(params.fetch(:id))
  end

  def check_permissions
    authorize User, :moderator?
  end
end
