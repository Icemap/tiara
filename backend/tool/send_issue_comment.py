#!/usr/bin/env python3

from typing import List, Dict, Optional
from backend.model import base
from backend.model.issue import ISSUE_TABLE_NAME, Issue
from backend.tool.logger import get_logger

logger = get_logger(__name__)


def search_similar_issues(issue: Issue, limit_per_field: int = 5) -> List[Dict]:
    """
    Search for similar issues using semantic vector search on title and body.
    
    Args:
        issue: The issue to find similar issues for
        limit_per_field: Number of results to get for each field (title_vec, body_vec)
        
    Returns:
        List of similar issues (as dicts) sorted by distance, deduplicated
    """
    if not issue.title and not issue.body:
        logger.warning(f"Issue #{issue.github_issue_number} has no title or body for similarity search")
        return []
    
    table = base.db.open_table(ISSUE_TABLE_NAME)
    all_results = []
    
    try:
        # Search by title vector if title exists
        if issue.title and issue.title.strip():
            logger.debug(f"Searching similar issues by title: '{issue.title[:50]}'")
            title_results = table.search(issue.title).limit(limit_per_field).vector_column("title_vec").to_list()
            
            for result in title_results:
                result['_search_field'] = 'title_vec'
                all_results.append(result)
            
            logger.debug(f"Found {len(title_results)} similar issues by title")
        
        # Search by body vector if body exists
        if issue.body and issue.body.strip():
            logger.debug(f"Searching similar issues by body: '{issue.body[:50]}...'")
            body_results = table.search(issue.body).limit(limit_per_field).vector_column("body_vec").to_list()
            
            for result in body_results:
                result['_search_field'] = 'body_vec'
                all_results.append(result)
            
            logger.debug(f"Found {len(body_results)} similar issues by body")
        
        # Deduplicate results by github_issue_id, keeping the one with smaller distance
        deduplicated_results = _deduplicate_by_distance(all_results, issue.github_issue_id)
        
        # Sort by distance (ascending - smaller distance means more similar)
        deduplicated_results.sort(key=lambda x: x.get('_distance', float('inf')))
        
        # Limit total results (title_vec + body_vec should each contribute up to limit_per_field)
        max_total_results = limit_per_field * 2
        final_results = deduplicated_results[:max_total_results]
        
        logger.info(f"Found {len(final_results)} similar issues for issue #{issue.github_issue_number}")
        
        if final_results:
            distances = [r.get('_distance', 'N/A') for r in final_results[:3]]
            logger.debug(f"Top 3 similarity distances: {distances}")
        
        return final_results
        
    except Exception as e:
        logger.error(f"Error searching similar issues for #{issue.github_issue_number}: {str(e)}")
        return []


def _deduplicate_by_distance(results: List[Dict], exclude_issue_id: Optional[int] = None) -> List[Dict]:
    """
    Deduplicate search results by github_issue_id, keeping the result with smaller distance.
    
    Args:
        results: List of search result dictionaries
        exclude_issue_id: Issue ID to exclude from results (usually the current issue)
        
    Returns:
        Deduplicated list of results
    """
    issue_map = {}
    
    for result in results:
        issue_id = result.get('github_issue_id')
        
        # Skip if no issue_id or if it's the same as the current issue
        if not issue_id or issue_id == exclude_issue_id:
            continue
        
        distance = result.get('_distance', float('inf'))
        
        # Keep the result with smaller distance
        if issue_id not in issue_map or distance < issue_map[issue_id].get('_distance', float('inf')):
            issue_map[issue_id] = result
    
    return list(issue_map.values())


def log_similar_issues(similar_issues: List[Dict], current_issue: Issue):
    """
    Log information about found similar issues.
    
    Args:
        similar_issues: List of similar issue dictionaries
        current_issue: The current issue being processed
    """
    if not similar_issues:
        logger.info(f"No similar issues found for #{current_issue.github_issue_number}")
        return
    
    logger.info(f"Found {len(similar_issues)} similar issues for #{current_issue.github_issue_number}:")
    
    for i, similar in enumerate(similar_issues[:5], 1):  # Log top 5
        issue_number = similar.get('github_issue_number', 'N/A')
        title = similar.get('title', 'N/A')
        distance = similar.get('_distance', 'N/A')
        search_field = similar.get('_search_field', 'unknown')
        state = similar.get('state', 'N/A')
        
        # Truncate title if too long
        display_title = title[:60] + "..." if len(str(title)) > 60 else title
        
        logger.info(f"  {i}. Issue #{issue_number} (distance: {distance:.4f}, field: {search_field}, state: {state})")
        logger.info(f"     Title: {display_title}")

if __name__ == "__main__":
    table = base.db.open_table(ISSUE_TABLE_NAME)
    results = table.search("test").limit(1).vector_column("title_vec").to_list()
    print(results)