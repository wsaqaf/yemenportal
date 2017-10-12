class PostsProxyController < ApplicationController
  def show
    render html: post.page_content.html_safe
  end

  private

  def post
    Post.find(params[:id])
  end
end
