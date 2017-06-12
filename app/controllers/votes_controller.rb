class VotesController < ApplicationController
  before_action :authenticate_user!
  respond_to :js, only: [:update]

  def update
    old_type = VoteService.make_vote(params, current_user)
    render json: { result: old_type }, status: :ok
  end
end
