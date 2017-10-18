class Posts::VotesController < ApplicationController
  before_action :authenticate_user!

  def update
    if params[:type] == "upvote"
      vote_updater.upvote
    elsif params[:type] == "downvote"
      vote_updater.downvote
    end
  end

  def destroy
    vote_updater.delete
  end

  private

  def vote_updater
    Posts::VoteUpdater.new(current_user, post)
  end

  def post
    ::Post.find(params[:post_id])
  end
end
