class Posts::ContentsController < ApplicationController
  def show
    render html: post_content
  end

  private

  def post_content
    HTTParty.get(post.link).body.html_safe
  end

  def post
    ::Post.find(params[:post_id])
  end
end
