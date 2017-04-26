class Sources::ApproveController < ApplicationController
  before_action :authenticate_user!
  before_action :find_source

  def update
    @source.update(approve_state: Source.approve_state.approved)
    redirect_to :back
  end

  private

  def find_source
    @source = Source.find(params.fetch(:id))
  end
end
