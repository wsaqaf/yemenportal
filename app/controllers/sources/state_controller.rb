class Sources::StateController < ApplicationController
  before_action :authenticate_user!, :check_permissions
  before_action :find_source

  def update
    @source.update(approve_state: new_state)
    redirect_to :back
  end

  private

  def find_source
    @source = Source.find(params.fetch(:id))
  end

  def check_permissions
    authorize User, :moderator?
  end

  def new_state
    Source.approve_state.approved
  end
end
