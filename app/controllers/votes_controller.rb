class VotesController < ApplicationController
  before_action :authenticate_user!
  respond_to :js, only: [:update]
  UPVOTE = "upvote".freeze
  BUTTON_TYPE = { upvote: "upvote", downvote: "downvote" }.freeze

  def update
    post = Post.find(params.fetch(:post_id))
    vote = Vote.find_by(user: current_user, post: post)
    type = params[:type] == UPVOTE

    if vote
      old_type = vote.positive ? BUTTON_TYPE[:upvote] : BUTTON_TYPE[:downvote]
      vote.positive == type ? vote.delete : vote.update(positive: type)
    else
      old_type = "new"
      Vote.create(user: current_user, positive: type, post: post)
    end

    render json: { result: old_type }, status: :ok
  end
end
