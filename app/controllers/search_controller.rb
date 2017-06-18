class SearchController < ApplicationController
  before_action :find_posts

  def index
    render cell: true, model: @posts, options: { user: current_user, user_votes: user_voted,
      request_text: search_params[:search_text] }
  end

  private

  def find_posts
    @posts = Post.approved_posts.fulltext_search(search_params[:search_text])
  end

  def user_voted
    posts_ids = @posts.ids
    current_user ? current_user.votes.votes_posts(posts_ids) : []
  end

  def search_params
    @_search_params ||= params.require(:search_form).permit(:search_text)
  end
end
