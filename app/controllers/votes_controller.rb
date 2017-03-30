class VotesController < ApplicationController
  before_action :authenticate_user!
  UPVOTE = "like".freeze

  def update
    post = Post.find(params.fetch(:post_id))
    unless Vote.find_by(user: current_user, post: post)
      Vote.create(user: current_user, positive: params[:type] == UPVOTE, post: post)
    end
  end
end
